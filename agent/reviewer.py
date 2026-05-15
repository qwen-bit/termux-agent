"""Self-reviewer — evaluates progress and decides next action."""
import json
from agent.llm import LLMClient

REVIEWER_SYSTEM = """You are a critical AI reviewer. You evaluate whether an autonomous agent
is making real progress toward a goal, and decide what should happen next.

Given the goal, the plan, and execution history, return a JSON object:
{
  "status": "on_track" | "needs_replan" | "completed" | "stuck",
  "progress_pct": 0-100,
  "assessment": "brief honest assessment",
  "next_action": "what the agent should do immediately next",
  "blockers": ["list of blockers if any"],
  "replan_reason": "why replan is needed (only if status=needs_replan)"
}"""


class Reviewer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(self, goal: str, plan: dict, history: list[dict]) -> dict:
        """Evaluate current progress."""
        prompt = (
            f"Goal: {goal}\n\n"
            f"Plan:\n{json.dumps(plan, indent=2)}\n\n"
            f"Execution history (last {min(len(history), 10)} steps):\n"
            f"{json.dumps(history[-10:], indent=2)}"
        )
        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM},
            {"role": "user", "content": prompt},
        ]
        resp = self.llm.chat(messages, temperature=0.1)
        content = resp["content"]

        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "status": "on_track",
                "progress_pct": 50,
                "assessment": content,
                "next_action": "Continue with plan",
                "blockers": [],
            }

    def is_goal_complete(self, goal: str, history: list[dict]) -> bool:
        """Quick check: has the goal been achieved?"""
        result = self.review(goal, {}, history)
        return result.get("status") == "completed"
