"""Memory skill — save and recall information."""
from skills.base import BaseSkill


class MemorySkill(BaseSkill):
    def __init__(self, memory=None):
        self.memory = memory

    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "memory_save",
                    "description": "Save a key-value fact to long-term memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key"},
                            "value": {"type": "string", "description": "Value to store"},
                        },
                        "required": ["key", "value"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "memory_recall",
                    "description": "Recall a fact from long-term memory by key.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key"},
                        },
                        "required": ["key"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "memory_list",
                    "description": "List all stored memory keys and values.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    def handles(self) -> list[str]:
        return ["memory_save", "memory_recall", "memory_list"]

    def call(self, name: str, arguments: dict) -> str:
        if not self.memory:
            return "[Memory disabled]"
        if name == "memory_save":
            self.memory.remember(arguments["key"], arguments["value"])
            return f"Saved: {arguments['key']} = {arguments['value']}"
        if name == "memory_recall":
            val = self.memory.recall(arguments["key"])
            return val if val is not None else f"[Not found] {arguments['key']}"
        if name == "memory_list":
            all_mem = self.memory.recall_all()
            if not all_mem:
                return "(memory is empty)"
            return "\n".join(f"{k}: {v}" for k, v in all_mem.items())
        return f"[ERROR] Unknown memory tool: {name}"
