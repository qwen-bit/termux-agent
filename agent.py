#!/usr/bin/env python3
"""
TermuxAgent — Autonomous terminal agent.
Usage: python agent.py "your goal here"
"""
import sys
import argparse
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.prompt import Prompt

console = Console()

BANNER = r"""
 _____ ____ __  __ _   ___  __     _    ____  _____ _   _ _____
|_   _| ___||  \/  | | | \ \/ /   / \  / ___|| ____| \ | |_   _|
  | | |___ \| |\/| | | | >\  /   / _ \| |  _ |  _| |  \| | | |
  | |  ___) | |  | | |_| |/  \  / ___ \ |_| || |___| |\  | | |
  |_| |____/|_|  |_|\___//_/\_\/_/   \_\____|_____|_| \_| |_|
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="TermuxAgent — Autonomous AI agent for your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "Set up a Python Flask server"
  python agent.py --verbose "Organize files in ~/Downloads"
  python agent.py --interactive
  python agent.py --auto-approve "Install and configure git"
        """,
    )
    parser.add_argument("goal", nargs="?", help="The goal for the agent to achieve")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode (prompt for goals)")
    parser.add_argument("-y", "--auto-approve", action="store_true", help="Auto-approve all shell/code commands")
    parser.add_argument("-n", "--max-steps", type=int, help="Max execution steps (default: from .env)")
    parser.add_argument("--list-skills", action="store_true", help="List available skills and exit")
    return parser.parse_args()


def list_skills():
    from skills import get_all_skills
    skills = get_all_skills()
    console.print("\n[bold]Available Skills:[/bold]\n")
    for skill in skills:
        defs = skill.definitions()
        console.print(f"  [cyan]{skill.__class__.__name__}[/cyan]")
        for d in defs:
            fn = d["function"]
            console.print(f"    • [green]{fn['name']}[/green] — {fn['description']}")
    console.print()


def check_env():
    """Verify .env exists and is configured."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        example = Path(__file__).parent / ".env.example"
        if example.exists():
            import shutil
            shutil.copy(example, env_file)
            console.print("[yellow]Created .env from .env.example — please add your OPENAI_API_KEY[/yellow]")
        else:
            console.print("[red].env file not found. Run: cp .env.example .env[/red]")
        sys.exit(1)

    from agent.config import config
    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Config error: {e}[/red]")
        sys.exit(1)


def run_agent(goal: str, verbose: bool, auto_approve: bool, max_steps: int | None):
    from agent.executor import AgentExecutor
    kwargs = {"verbose": verbose, "auto_approve": auto_approve}
    if max_steps:
        kwargs["max_steps"] = max_steps
    executor = AgentExecutor(**kwargs)
    executor.run(goal)


def main():
    args = parse_args()

    console.print(f"[bold cyan]{BANNER}[/bold cyan]")

    if args.list_skills:
        list_skills()
        return

    check_env()

    if args.interactive:
        console.print("[bold]Interactive mode — type your goal, or 'quit' to exit.[/bold]\n")
        while True:
            goal = Prompt.ask("[bold cyan]Goal[/bold cyan]").strip()
            if goal.lower() in ("quit", "exit", "q"):
                break
            if goal:
                run_agent(goal, args.verbose, args.auto_approve, args.max_steps)
                console.print("\n[dim]Ready for next goal.[/dim]\n")
    elif args.goal:
        run_agent(args.goal, args.verbose, args.auto_approve, args.max_steps)
    else:
        console.print("[yellow]No goal provided. Use: python agent.py \"your goal\"[/yellow]")
        console.print("  or: python agent.py --interactive")
        console.print("  or: python agent.py --help")


if __name__ == "__main__":
    main()
