"""Agent executor — the main loop that runs steps and calls tools."""
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.text import Text

from agent.config import config
from agent.llm import LLMClient
from agent.planner import Planner
from agent.reviewer import Reviewer
from agent.memory import Memory
from skills import get_all_skills, build_tool_definitions, dispatch

console = Console()

AGENT_SYSTEM = """You are TermuxAgent, a powerful autonomous AI agent running in a terminal.
You have been given a goal and a plan. Execute the plan step by step using your tools.

Guidelines:
- Use tools to take real actions — don't just describe what you would do
- Check results after each action and adapt
- Be efficient: complete steps in the fewest tool calls needed
- If something fails, try an alternative approach
- When the goal is fully achieved, say "GOAL_COMPLETE: <summary>"
- When you are permanently stuck and can't proceed, say "GOAL_FAILED: <reason>"

You have access to: shell commands, file operations, web fetching, memory, device control, and code execution."""


class AgentExecutor:
    def __init__(self, verbose: bool = False, auto_approve: bool = False, max_steps: int = None):
        self.verbose = verbose or config.VERBOSE
        self.auto_approve = auto_approve or config.AUTO_APPROVE_SHELL
        self.max_steps = max_steps or config.MAX_STEPS

        self.llm = LLMClient()
        self.planner = Planner(self.llm)
        self.reviewer = Reviewer(self.llm)
        self.memory = Memory() if config.MEMORY_ENABLED else None

        self.skills = get_all_skills(memory=self.memory, auto_approve=self.auto_approve)
        self.tools = build_tool_definitions(self.skills)

    def run(self, goal: str):
        """Run the agent toward a goal."""
        console.print(Panel(f"[bold cyan]Goal:[/bold cyan] {goal}", title="TermuxAgent"))

        # Start memory session
        session_id = None
        if self.memory:
            session_id = self.memory.start_session(goal)

        # === PLAN ===
        console.print("\n[bold yellow]Planning...[/bold yellow]")
        prior_ctx = ""
        if self.memory:
            prior_ctx = self.memory.recent_sessions_summary(3)

        plan = self.planner.create_plan(goal, prior_ctx)
        console.print(Panel(
            "\n".join(f"  {s['id']}. {s['action']}" for s in plan.get("steps", [])),
            title=f"[green]Plan: {plan.get('goal_summary', goal)}[/green]",
        ))

        # === EXECUTE ===
        messages = [
            {"role": "system", "content": AGENT_SYSTEM},
            {"role": "user", "content": (
                f"Goal: {goal}\n\n"
                f"Plan:\n{json.dumps(plan, indent=2)}\n\n"
                "Begin executing the plan now. Use tools to take real actions."
            )},
        ]

        history: list[dict] = []
        step = 0
        completed = False
        replan_count = 0
        MAX_REPLANS = 2

        while step < self.max_steps and not completed:
            step += 1
            console.print(f"\n[dim]── Step {step}/{self.max_steps} ──[/dim]")

            # Periodic review every 5 steps
            if step > 1 and step % 5 == 0 and replan_count < MAX_REPLANS:
                console.print("[yellow]Reviewing progress...[/yellow]")
                review = self.reviewer.review(goal, plan, history)
                status = review.get("status", "on_track")
                pct = review.get("progress_pct", 0)
                console.print(f"  Status: [bold]{status}[/bold] | Progress: {pct}%")
                console.print(f"  {review.get('assessment', '')}")

                if status == "completed":
                    console.print("\n[bold green]Reviewer confirms: GOAL COMPLETE[/bold green]")
                    completed = True
                    break
                elif status in ("needs_replan", "stuck"):
                    replan_count += 1
                    console.print(f"[yellow]Replanning (attempt {replan_count})...[/yellow]")
                    completed_steps = [h for h in history if h.get("type") == "tool_result"]
                    plan = self.planner.replan(goal, completed_steps, {}, review.get("assessment", ""))
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Replanned. New plan:\n{json.dumps(plan, indent=2)}\n"
                            "Continue from where you left off."
                        ),
                    })

            # Call LLM
            try:
                resp = self.llm.chat(messages, tools=self.tools)
            except Exception as e:
                console.print(f"[red]LLM error: {e}[/red]")
                time.sleep(2)
                continue

            content = resp.get("content", "")
            tool_calls = resp.get("tool_calls", [])

            # Check for completion signal in content
            if content:
                if self.verbose:
                    console.print(f"[dim]{content}[/dim]")
                if "GOAL_COMPLETE" in content:
                    console.print(Panel(f"[bold green]{content}[/bold green]", title="Complete"))
                    completed = True
                    break
                if "GOAL_FAILED" in content:
                    console.print(Panel(f"[bold red]{content}[/bold red]", title="Failed"))
                    break

            # Add assistant turn
            messages.append({"role": "assistant", "content": content or None, "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])}}
                for tc in tool_calls
            ] if tool_calls else None})

            if not tool_calls:
                # No tools called — push agent to act
                if content:
                    messages.append({
                        "role": "user",
                        "content": "Good. Now take the next action using your tools to make real progress.",
                    })
                continue

            # Execute tool calls
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["arguments"]
                console.print(f"  [cyan]Tool:[/cyan] {tool_name}({_fmt_args(tool_args)})")

                result = dispatch(self.skills, tool_name, tool_args)

                if self.verbose:
                    if len(result) > 500:
                        console.print(f"  [dim]{result[:500]}...[/dim]")
                    else:
                        console.print(f"  [dim]{result}[/dim]")

                history.append({"type": "tool_result", "tool": tool_name, "result": result[:300]})
                if session_id and self.memory:
                    self.memory.log_event(session_id, "tool", {"tool": tool_name, "result": result[:200]})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        # Final review
        if not completed:
            console.print("\n[yellow]Running final review...[/yellow]")
            review = self.reviewer.review(goal, plan, history)
            status = review.get("status")
            if status == "completed":
                console.print(Panel(
                    f"[green]{review.get('assessment', 'Goal achieved.')}[/green]",
                    title="Complete",
                ))
            else:
                console.print(Panel(
                    f"[yellow]{review.get('assessment', 'Max steps reached.')}[/yellow]",
                    title=f"Status: {status}",
                ))

        console.print("\n[dim]Session complete.[/dim]")


def _fmt_args(args: dict) -> str:
    """Format tool arguments for display."""
    parts = []
    for k, v in args.items():
        sv = str(v)
        if len(sv) > 60:
            sv = sv[:60] + "..."
        parts.append(f"{k}={repr(sv)}")
    return ", ".join(parts)
