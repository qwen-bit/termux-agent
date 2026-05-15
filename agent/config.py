"""Agent configuration loader."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    MODEL: str = os.getenv("MODEL", "google/gemma-3-27b-it:free")
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
                "OPENAI_API_KEY is not set.\n"
                "  1. Get a FREE API key at https://openrouter.ai/keys\n"
                "  2. Copy .env.example to .env\n"
                "  3. Set OPENAI_API_KEY=your_key_here\n"
                "  Free models included: google/gemma-3-27b-it:free, deepseek/deepseek-r1:free"
            )


config = Config()
