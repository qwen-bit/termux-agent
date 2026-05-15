"""Device skill — Termux device control (vibrate, notify, clipboard, battery, etc.)."""
import subprocess
import shutil
from skills.base import BaseSkill


def _termux(cmd: list[str], fallback: str = "") -> str:
    """Run a termux-api command, return stdout or fallback."""
    if shutil.which(cmd[0]) is None:
        return f"[Termux API not available] Would run: {' '.join(cmd)}"
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() or r.stderr.strip() or "(ok)"
    except Exception as e:
        return f"[ERROR] {e}"


class DeviceSkill(BaseSkill):
    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "device_notify",
                    "description": "Send a notification to the device.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "message": {"type": "string"},
                        },
                        "required": ["title", "message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_vibrate",
                    "description": "Vibrate the device.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration_ms": {
                                "type": "integer",
                                "description": "Duration in milliseconds (default 500)",
                            }
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_clipboard_set",
                    "description": "Copy text to the device clipboard.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to copy"}
                        },
                        "required": ["text"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_clipboard_get",
                    "description": "Get text from the device clipboard.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_battery",
                    "description": "Get device battery status.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_info",
                    "description": "Get general device/system information.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "device_tts",
                    "description": "Speak text aloud via text-to-speech.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to speak"}
                        },
                        "required": ["text"],
                    },
                },
            },
        ]

    def handles(self) -> list[str]:
        return [
            "device_notify",
            "device_vibrate",
            "device_clipboard_set",
            "device_clipboard_get",
            "device_battery",
            "device_info",
            "device_tts",
        ]

    def call(self, name: str, arguments: dict) -> str:
        if name == "device_notify":
            return _termux([
                "termux-notification",
                "-t", arguments["title"],
                "-c", arguments["message"],
            ])
        if name == "device_vibrate":
            ms = arguments.get("duration_ms", 500)
            return _termux(["termux-vibrate", "-d", str(ms)])
        if name == "device_clipboard_set":
            return _termux(["termux-clipboard-set", arguments["text"]])
        if name == "device_clipboard_get":
            return _termux(["termux-clipboard-get"])
        if name == "device_battery":
            return _termux(["termux-battery-status"])
        if name == "device_info":
            # Fallback to uname when no Termux API
            import platform
            return (
                f"OS: {platform.system()} {platform.release()}\n"
                f"Machine: {platform.machine()}\n"
                f"Python: {platform.python_version()}"
            )
        if name == "device_tts":
            result = _termux(["termux-tts-speak", arguments["text"]])
            if "not available" in result:
                # Fallback: espeak
                try:
                    subprocess.run(["espeak", arguments["text"]], timeout=10)
                    return "(spoken via espeak)"
                except Exception:
                    return f"[TTS unavailable] Would say: {arguments['text']}"
            return result
        return f"[ERROR] Unknown device tool: {name}"
