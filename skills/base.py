"""Base class for all skills."""
from abc import ABC, abstractmethod


class BaseSkill(ABC):
    @abstractmethod
    def definitions(self) -> list[dict]:
        """Return OpenAI tool definitions for this skill."""
        ...

    @abstractmethod
    def handles(self) -> list[str]:
        """Return list of tool names this skill handles."""
        ...

    @abstractmethod
    def call(self, name: str, arguments: dict) -> str:
        """Execute a tool call and return string result."""
        ...
