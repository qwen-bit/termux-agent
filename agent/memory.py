"""Persistent memory — short and long term."""
import json
import time
from pathlib import Path
from agent.config import config


class Memory:
    def __init__(self):
        self.path = config.MEMORY_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {"sessions": [], "long_term": {}}

    def _save(self):
        self.path.write_text(json.dumps(self._data, indent=2))

    # ── Session memory ──────────────────────────────────────────────────────

    def start_session(self, goal: str) -> str:
        session_id = f"session_{int(time.time())}"
        self._data["sessions"].append({
            "id": session_id,
            "goal": goal,
            "started_at": time.time(),
            "events": [],
        })
        self._save()
        return session_id

    def log_event(self, session_id: str, event_type: str, data: dict):
        for s in self._data["sessions"]:
            if s["id"] == session_id:
                s["events"].append({
                    "type": event_type,
                    "ts": time.time(),
                    **data,
                })
                break
        self._save()

    def get_session(self, session_id: str) -> dict | None:
        for s in self._data["sessions"]:
            if s["id"] == session_id:
                return s
        return None

    # ── Long-term memory ────────────────────────────────────────────────────

    def remember(self, key: str, value: str):
        self._data["long_term"][key] = {"value": value, "ts": time.time()}
        self._save()

    def recall(self, key: str) -> str | None:
        entry = self._data["long_term"].get(key)
        return entry["value"] if entry else None

    def recall_all(self) -> dict:
        return {k: v["value"] for k, v in self._data["long_term"].items()}

    def forget(self, key: str):
        self._data["long_term"].pop(key, None)
        self._save()

    # ── Recent context ──────────────────────────────────────────────────────

    def recent_sessions_summary(self, n: int = 3) -> str:
        recent = self._data["sessions"][-n:]
        if not recent:
            return "No prior sessions."
        lines = []
        for s in recent:
            lines.append(f"- Goal: {s['goal']} ({len(s['events'])} events)")
        return "\n".join(lines)
