"""Skill registry — all tools the agent can call."""
from skills.shell import ShellSkill
from skills.file import FileSkill
from skills.web import WebSkill
from skills.memory_skill import MemorySkill
from skills.device import DeviceSkill
from skills.code import CodeSkill


def get_all_skills(memory=None, auto_approve: bool = False):
    """Return all skill instances."""
    return [
        ShellSkill(auto_approve=auto_approve),
        FileSkill(),
        WebSkill(),
        MemorySkill(memory=memory),
        DeviceSkill(),
        CodeSkill(auto_approve=auto_approve),
    ]


def build_tool_definitions(skills: list) -> list[dict]:
    """Build OpenAI-compatible tool definitions from all skills."""
    tools = []
    for skill in skills:
        tools.extend(skill.definitions())
    return tools


def dispatch(skills: list, name: str, arguments: dict) -> str:
    """Route a tool call to the right skill."""
    for skill in skills:
        if name in skill.handles():
            return skill.call(name, arguments)
    return f"[ERROR] Unknown tool: {name}"
