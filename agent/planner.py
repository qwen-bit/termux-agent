"""Strategic planner — breaks goals into actionable plans."""
import json
from agent.llm import LLMClient

PLANNER_SYSTEM = """You are a strategic AI planner. Given a goal, you produce a clear, ordered,
step-by-step action plan that an autonomous agent will execute.

Rules:
- Each step must be specific and actionable
- Steps should be sequenced logically
- Anticipate dependencies and blockers
- Include verification/review steps
- Keep steps concise but unambiguous
- Aim for 3–10 steps (more for complex goals)

Return a JSON object like:
{
  "goal_summary": "one-line restatement of goal",
  "steps": [
    {"id": 1, "action": "...", "rationale": "...", "depends_on": []},
    ...
  ],
  "success_criteria": "How we know the goal is achieved"
}"""


class Planner:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def create_plan(self, goal: str, context: str = "") -> dict:
        """Generate an initial plan for a goal."""
        prompt = f"Goal: {goal}"
        if context:
            prompt += f"\n\nContext / prior state:\n{context}"

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": prompt},
        ]
        resp = self.llm.chat(messages, temperature=0.2)
        content = resp["content"]

        # Strip markdown code fences if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: wrap raw text
            return {
                "goal_summary": goal,
                "steps": [{"id": 1, "action": content, "rationale": "LLM plan", "depends_on": []}],
                "success_criteria": "Goal completed",
            }

    def replan(self, goal: str, completed_steps: list, failed_step: dict, error: str) -> dict:
        """Replan after a failure."""
        context = (
            f"Completed so far: {json.dumps(completed_steps)}\n"
            f"Failed step: {json.dumps(failed_step)}\n"
            f"Error: {error}\n"
            "Please create a revised plan to continue toward the goal."
        )
        return self.create_plan(goal, context)
