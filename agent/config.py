"""Agent configuration loader."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL: str = os.getenv("MODEL", "gpt-4o")
    MAX_STEPS: int = int(os.getenv("MAX_STEPS", "20"))
    MEMORY_ENABLED: bool = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
    VERBOSE: bool = os.getenv("VERBOSE", "false").lower() == "true"
    AUTO_APPROVE_SHELL: bool = os.getenv("AUTO_APPROVE_SHELL", "false").lower() == "true"
    TERMUX_API: bool = os.getenv("TERMUX_API", "false").lower() == "true"

    PROJECT_ROOT: Path = Path(__file__).parent.parent
    MEMORY_FILE: Path = PROJECT_ROOT / "memory" / "memory.json"
    LOG_DIR: Path = PROJECT_ROOT / "logs"

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
            )


config = Config()
