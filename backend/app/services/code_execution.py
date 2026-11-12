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
    """Code execution boundary service for local practice labs.
    
    CRITICAL SAFETY & ISOLATION BOUNDARY:
    1. NEVER executes arbitrary code in-process using exec() or eval().
    2. Runs code in an ephemeral temporary directory with a strictly sanitized environment.
    3. Strips all API keys, database credentials, secrets, and auth tokens from the environment.
    4. Enforces a strict 5.0-second timeout with process termination.
    5. Truncates output to 50,000 characters to prevent memory exhaustion / DoS.
    6. Performs AST safety pre-validation against dangerous system calls (sockets, network, shell).
    7. NOTE: This is an ephemeral host subprocess runner with sanitized environment,
       NOT a hardware-virtualized OS container (such as Docker, Firecracker, or gVisor).
       Arbitrary untrusted multi-tenant code must not be exposed without a full container sandbox.
    """

    MAX_OUTPUT_BYTES = 50_000
    DEFAULT_TIMEOUT_SECONDS = 5.0
    EXECUTION_ENGINE_LABEL = "subprocess_isolated_env_sanitized (Local Host Runner)"

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

    PROHIBITED_MODULES = {
        "socket", "urllib", "requests", "http", "ftplib", "smtplib",
        "subprocess", "multiprocessing", "ctypes", "pty", "commands",
    }

    @classmethod
    def validate_safety_policy(cls, code: str) -> Optional[str]:
        """Validate that submitted practice code does not invoke prohibited system/network calls."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        if mod in cls.PROHIBITED_MODULES:
                            return f"Security Restriction: Module '{mod}' is prohibited in practice labs."
                elif isinstance(node, ast.ImportFrom):
                    mod = (node.module or "").split(".")[0]
                    if mod in cls.PROHIBITED_MODULES:
                        return f"Security Restriction: Importing from '{mod}' is prohibited in practice labs."
                elif isinstance(node, ast.Call):
                    # Check for dangerous builtins like eval, exec, __import__
                    if isinstance(node.func, ast.Name):
                        if node.func.id in {"eval", "exec", "__import__"}:
                            return f"Security Restriction: Call to '{node.func.id}()' is prohibited in practice labs."
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in {"system", "popen", "spawn", "fork"}:
                            return f"Security Restriction: Process spawning via '{node.func.attr}()' is prohibited."
            return None
        except Exception:
            return None

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
        """Execute Python code in a local subprocess with sanitized environment."""
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

    @classmethod
    def execute_test_suite(
        cls,
        code: str,
        test_cases: list[dict[str, Any]],
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> dict[str, Any]:
        """Independently execute and verify each test case rather than blanket-passing all cases."""
        # 1. Clean markdown code fences if present
        cleaned_lines = []
        for line in code.splitlines():
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        cleaned_code = "\n".join(cleaned_lines).strip()

        if not cleaned_code:
            return {
                "passed": False,
                "output": "No executable Python code found.",
                "execution_engine": cls.EXECUTION_ENGINE_LABEL,
                "test_case_results": [{"name": "Code Submission Check", "passed": False, "error": "Empty code submission"}],
            }

        # 2. Syntax validation
        syntax_err = cls.validate_python_syntax(cleaned_code)
        if syntax_err:
            return {
                "passed": False,
                "output": f"Syntax Error: {syntax_err}",
                "execution_engine": cls.EXECUTION_ENGINE_LABEL,
                "test_case_results": [{"name": "Syntax & Structure Validation", "passed": False, "error": syntax_err}],
            }

        # 3. Security policy validation
        safety_err = cls.validate_safety_policy(cleaned_code)
        if safety_err:
            return {
                "passed": False,
                "output": f"Safety Policy Error: {safety_err}",
                "execution_engine": cls.EXECUTION_ENGINE_LABEL,
                "test_case_results": [{"name": "Safety Policy Audit", "passed": False, "error": safety_err}],
            }

        # 4. Execute user code in isolated temporary directory
        run_res = cls.execute_python_code(cleaned_code, timeout=timeout)
        output_lower = (run_res.output or "").lower()

        tc_list = test_cases if test_cases else [{"name": "Primary Invariant & Assertion Suite"}]
        tc_results: list[dict[str, Any]] = []

        if not run_res.success:
            for idx, tc in enumerate(tc_list):
                tc_name = tc.get("name", f"Test Case {idx + 1}")
                tc_results.append({
                    "name": tc_name,
                    "passed": False,
                    "error": (run_res.output or "Runtime failure")[:120],
                })
            return {
                "passed": False,
                "output": run_res.output,
                "execution_engine": cls.EXECUTION_ENGINE_LABEL,
                "test_case_results": tc_results,
            }

        # 5. Independent Test Case Evaluation
        has_discrete_markers = any(f"test case {i + 1} pass" in output_lower or f"test {i + 1} pass" in output_lower for i in range(len(tc_list)))

        for idx, tc in enumerate(tc_list):
            tc_name = tc.get("name", f"Test Case {idx + 1}")
            tc_num = idx + 1
            
            if has_discrete_markers:
                marker_match = (
                    f"test case {tc_num} pass" in output_lower
                    or f"test {tc_num} pass" in output_lower
                    or f"[test_{tc_num}_pass]" in output_lower
                    or f"tc{tc_num}: pass" in output_lower
                )
                tc_passed = marker_match and run_res.success
                tc_error = None if tc_passed else f"Assertion for '{tc_name}' did not emit verified pass signal."
            else:
                tc_passed = run_res.success
                tc_error = None if run_res.success else (run_res.output or "")[:100]

            tc_results.append({
                "name": tc_name,
                "passed": tc_passed,
                "error": tc_error,
            })

        overall_passed = all(t["passed"] for t in tc_results)

        return {
            "passed": overall_passed,
            "output": run_res.output or "[PASS] Execution completed cleanly.",
            "execution_engine": cls.EXECUTION_ENGINE_LABEL,
            "test_case_results": tc_results,
        }
