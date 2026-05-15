"""Shell skill — execute terminal commands."""
import subprocess
import sys
from skills.base import BaseSkill


class ShellSkill(BaseSkill):
    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve

    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "shell_run",
                    "description": (
                        "Execute a shell command in the terminal. "
                        "Use for installing packages, running scripts, checking system state, etc."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The shell command to run",
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default 60)",
                                "default": 60,
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Working directory (optional)",
                            },
                        },
                        "required": ["command"],
                    },
                },
            }
        ]

    def handles(self) -> list[str]:
        return ["shell_run"]

    def call(self, name: str, arguments: dict) -> str:
        command = arguments["command"]
        timeout = arguments.get("timeout", 60)
        cwd = arguments.get("working_dir")

        if not self.auto_approve:
            print(f"\n[Shell] Requesting to run: {command}")
            ans = input("  Approve? [y/N] ").strip().lower()
            if ans not in ("y", "yes"):
                return "[DENIED] Command was not approved by user."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            output = result.stdout.strip()
            stderr = result.stderr.strip()
            combined = []
            if output:
                combined.append(f"STDOUT:\n{output}")
            if stderr:
                combined.append(f"STDERR:\n{stderr}")
            if result.returncode != 0:
                combined.append(f"Exit code: {result.returncode}")
            return "\n".join(combined) if combined else "(no output)"
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Command exceeded {timeout}s"
        except Exception as e:
            return f"[ERROR] {e}"
