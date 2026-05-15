"""Code skill — write and run Python/bash code snippets."""
import subprocess
import tempfile
import os
from pathlib import Path
from skills.base import BaseSkill


class CodeSkill(BaseSkill):
    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve

    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "code_run_python",
                    "description": "Write and execute a Python script, returning its output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Python code to run"},
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout seconds (default 30)",
                            },
                        },
                        "required": ["code"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "code_run_bash",
                    "description": "Write and execute a bash script, returning its output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Bash script to run"},
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout seconds (default 30)",
                            },
                        },
                        "required": ["code"],
                    },
                },
            },
        ]

    def handles(self) -> list[str]:
        return ["code_run_python", "code_run_bash"]

    def call(self, name: str, arguments: dict) -> str:
        code = arguments["code"]
        timeout = arguments.get("timeout", 30)
        lang = "Python" if name == "code_run_python" else "Bash"

        if not self.auto_approve:
            print(f"\n[Code] Requesting to run {lang}:\n---\n{code[:300]}\n---")
            ans = input("  Approve? [y/N] ").strip().lower()
            if ans not in ("y", "yes"):
                return "[DENIED] Code execution not approved."

        suffix = ".py" if name == "code_run_python" else ".sh"
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(code)
            tmp = f.name

        try:
            cmd = ["python3", tmp] if name == "code_run_python" else ["bash", tmp]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            stderr = result.stderr.strip()
            parts = []
            if output:
                parts.append(output)
            if stderr:
                parts.append(f"STDERR: {stderr}")
            if result.returncode != 0:
                parts.append(f"Exit code: {result.returncode}")
            return "\n".join(parts) if parts else "(no output)"
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Exceeded {timeout}s"
        except Exception as e:
            return f"[ERROR] {e}"
        finally:
            os.unlink(tmp)
