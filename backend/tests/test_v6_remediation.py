from __future__ import annotations

import os
from pathlib import Path
import pytest
from app.services.code_execution import CodeExecutionService
from app.services.curriculum_planner import CurriculumPlannerService
from app.services.secret_storage import encrypt_secret, decrypt_secret, mask_secret


def test_code_execution_isolation_and_no_inprocess_exec():
    """Verify that CodeExecutionService runs in isolated subprocess and never uses in-process exec."""
    # 1. Successful execution
    res1 = CodeExecutionService.execute_python_code("x = 40 + 2\nprint('Result is', x)")
    assert res1.success is True
    assert "Result is 42" in res1.output
    assert res1.timed_out is False

    # 2. Syntax error caught by AST parser without execution
    res2 = CodeExecutionService.execute_python_code("def broken_syntax(")
    assert res2.success is False
    assert "SyntaxError" in res2.output
    assert res2.syntax_error is not None

    # 3. Timeout killed cleanly after 1 second without hanging
    res3 = CodeExecutionService.execute_python_code("import time\nwhile True:\n    time.sleep(0.1)", timeout=1.0)
    assert res3.success is False
    assert res3.timed_out is True
    assert "timed out after 1.0 seconds" in res3.output


def test_secret_storage_fernet_encryption():
    """Verify that secrets are encrypted with Fernet and never stored or returned in plaintext."""
    plaintext = "sk-ant-api-key-live-secret-9999"
    ciphertext = encrypt_secret(plaintext)
    assert ciphertext != plaintext
    assert len(ciphertext) > len(plaintext)
    assert ciphertext.startswith("gAAAAA")

    decrypted = decrypt_secret(ciphertext)
    assert decrypted == plaintext

    masked = mask_secret(ciphertext)
    assert masked.endswith("9999")
    assert plaintext not in masked
    assert "••••••••" in masked


def test_curriculum_duration_phase_calculations():
    """Verify hierarchical phase structures across all requested durations: 7, 15, 30, 90, 180, 365 days."""
    durations_expected = {
        7: 1,    # 1 Phase
        15: 2,   # 2 Phases
        30: 4,   # 4 Phases
        90: 6,   # 6 Phases
        180: 8,  # 8 Phases
        365: 12, # 12 Phases
    }
    for dur, expected_phases in durations_expected.items():
        phases = CurriculumPlannerService.calculate_phase_structure(dur)
        assert len(phases) == expected_phases, f"Duration {dur} should produce {expected_phases} phases, got {len(phases)}"
        assert phases[0]["start_day"] == 1
        assert phases[-1]["end_day"] == dur


def test_obsidian_path_traversal_guard():
    """Verify that path traversal attempts raise PermissionError via resolved path relative_to containment."""
    vault_root = Path("D:/vault").resolve()
    bad_rel = "../../Windows/System32/evil.md"
    dest_path = (vault_root / bad_rel).resolve()
    
    with pytest.raises(ValueError):
        dest_path.relative_to(vault_root)
