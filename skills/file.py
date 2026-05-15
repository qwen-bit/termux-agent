"""File skill — read, write, list, search files."""
import os
import json
from pathlib import Path
from skills.base import BaseSkill


class FileSkill(BaseSkill):
    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "file_read",
                    "description": "Read the contents of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to read"},
                            "max_chars": {
                                "type": "integer",
                                "description": "Max chars to return (default 8000)",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_write",
                    "description": "Write content to a file (creates or overwrites).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to write"},
                            "content": {"type": "string", "description": "Content to write"},
                            "append": {
                                "type": "boolean",
                                "description": "Append instead of overwrite (default false)",
                            },
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_list",
                    "description": "List files and directories at a path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path"},
                            "recursive": {
                                "type": "boolean",
                                "description": "List recursively (default false)",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_delete",
                    "description": "Delete a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to delete"},
                        },
                        "required": ["path"],
                    },
                },
            },
        ]

    def handles(self) -> list[str]:
        return ["file_read", "file_write", "file_list", "file_delete"]

    def call(self, name: str, arguments: dict) -> str:
        if name == "file_read":
            return self._read(**arguments)
        if name == "file_write":
            return self._write(**arguments)
        if name == "file_list":
            return self._list(**arguments)
        if name == "file_delete":
            return self._delete(**arguments)
        return f"[ERROR] Unknown file tool: {name}"

    def _read(self, path: str, max_chars: int = 8000) -> str:
        try:
            p = Path(path).expanduser()
            content = p.read_text(errors="replace")
            if len(content) > max_chars:
                content = content[:max_chars] + f"\n... [truncated at {max_chars} chars]"
            return content
        except Exception as e:
            return f"[ERROR] {e}"

    def _write(self, path: str, content: str, append: bool = False) -> str:
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            p.open(mode).write(content)
            return f"Written {len(content)} chars to {path}"
        except Exception as e:
            return f"[ERROR] {e}"

    def _list(self, path: str, recursive: bool = False) -> str:
        try:
            p = Path(path).expanduser()
            if recursive:
                entries = [str(e.relative_to(p)) for e in sorted(p.rglob("*"))]
            else:
                entries = sorted(os.listdir(p))
            return "\n".join(entries) if entries else "(empty)"
        except Exception as e:
            return f"[ERROR] {e}"

    def _delete(self, path: str) -> str:
        try:
            Path(path).expanduser().unlink()
            return f"Deleted {path}"
        except Exception as e:
            return f"[ERROR] {e}"
