from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CodeExecutionResult:
    success: bool
    output: str
    exit_code: Optional[int] = None
    timed_out: bool = False
    syntax_error: Optional[str] = None
    manual_run_command: str = ""
    error_type: Optional[str] = None


class CodeExecutionService:
    """Secure code execution boundary service.
    
    CRITICAL SAFETY RULES:
    1. NEVER executes arbitrary code in-process using exec() or eval().
    2. Runs code in an isolated ephemeral directory with a strictly sanitized environment.
    3. Strips all API keys, database credentials, secrets, and auth tokens from the environment.
    4. Enforces a strict 5.0-second timeout with process termination.
    5. Truncates output to 50,000 characters to prevent memory exhaustion / DoS.
    6. If execution fails, provides an exact terminal command for manual verification.
    """

    MAX_OUTPUT_BYTES = 50_000
    DEFAULT_TIMEOUT_SECONDS = 5.0

    # Whitelist of environment keys safe for runtime execution
    SAFE_ENV_KEYS = {
        "SYSTEMROOT",
        "SYSTEMDRIVE",
        "COMSPEC",
        "PATH",
        "PYTHONIOENCODING",
        "PYTHONUNBUFFERED",
        "TEMP",
        "TMP",
        "APPDATA",
        "LOCALAPPDATA",
    }

    @classmethod
    def _create_clean_env(cls, temp_dir: str) -> dict[str, str]:
        clean: dict[str, str] = {}
        for k in cls.SAFE_ENV_KEYS:
            val = os.environ.get(k)
            if val:
                clean[k] = val

        # Explicitly set UTF-8 encoding and isolated temp paths
        clean["PYTHONIOENCODING"] = "utf-8"
        clean["PYTHONUNBUFFERED"] = "1"
        clean["TEMP"] = temp_dir
        clean["TMP"] = temp_dir

        # Strip anything containing sensitive substrings
        sensitive_keywords = ["SECRET", "KEY", "TOKEN", "PASSWORD", "DATABASE", "AUTH", "AXIOM", "GEMINI", "OLLAMA"]
        clean = {
            k: v for k, v in clean.items()
            if not any(kw in k.upper() for kw in sensitive_keywords)
        }
        return clean

    @classmethod
    def validate_python_syntax(cls, code: str) -> Optional[str]:
        """Validate Python syntax without executing the code."""
        try:
            ast.parse(code)
            return None
        except SyntaxError as se:
            return f"SyntaxError at line {se.lineno}, col {se.offset}: {se.msg}"
        except Exception as exc:
            return f"Parse error: {type(exc).__name__}: {exc}"

    @classmethod
    def execute_python_code(
        cls,
        code: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        entry_file_name: str = "solution.py",
    ) -> CodeExecutionResult:
        """Execute Python code in an isolated subprocess sandbox."""
        # 1. Clean markdown code fences if present
        cleaned_lines = []
        for line in code.splitlines():
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        cleaned_code = "\n".join(cleaned_lines).strip()

        if not cleaned_code:
            return CodeExecutionResult(
                success=False,
                output="No executable Python code found.",
                syntax_error="Empty code submission",
                error_type="EmptySubmission",
            )

        # 2. Syntax check without execution
        syntax_err = cls.validate_python_syntax(cleaned_code)
        if syntax_err:
            return CodeExecutionResult(
                success=False,
                output=syntax_err,
                syntax_error=syntax_err,
                error_type="SyntaxError",
            )

        temp_dir = tempfile.mkdtemp(prefix="axiom_sandbox_")
        target_file = Path(temp_dir) / entry_file_name
        manual_cmd = f"python {target_file.name}"

        try:
            target_file.write_text(cleaned_code, encoding="utf-8")
            clean_env = cls._create_clean_env(temp_dir)

            # 3. Subprocess execution
            proc = subprocess.run(
                [sys.executable, str(target_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=clean_env,
                timeout=timeout,
                check=False,
            )

            stdout = (proc.stdout or "").strip()
            stderr = (proc.stderr or "").strip()

            combined = stdout
            if stderr:
                combined = f"{stdout}\n{stderr}".strip() if stdout else stderr

            if len(combined) > cls.MAX_OUTPUT_BYTES:
                combined = combined[:cls.MAX_OUTPUT_BYTES] + "\n...[Output truncated at 50,000 characters]"

            is_success = proc.returncode == 0
            return CodeExecutionResult(
                success=is_success,
                output=combined or ("Execution finished with exit code 0." if is_success else f"Process exited with code {proc.returncode}."),
                exit_code=proc.returncode,
                timed_out=False,
                manual_run_command=manual_cmd,
                error_type=None if is_success else "RuntimeError",
            )

        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                output=f"Execution timed out after {timeout:.1f} seconds. Infinite loop or compute budget exceeded.",
                exit_code=None,
                timed_out=True,
                manual_run_command=manual_cmd,
                error_type="TimeoutExpired",
            )
        except Exception as exc:
            return CodeExecutionResult(
                success=False,
                output=f"Execution boundary error: {type(exc).__name__}: {exc}",
                exit_code=None,
                manual_run_command=manual_cmd,
                error_type=type(exc).__name__,
            )
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
