# TermuxAgent 🤖

A powerful autonomous AI agent that runs in the terminal / Termux on Android. Give it a goal — it plans, acts, reviews, and iterates until done.

## Features

- **Strategic Planner** — Breaks goals into actionable step-by-step plans
- **Skill System** — Pluggable skills: shell, file, web, device, memory
- **Self-Reviewer** — Reviews progress and replans if stuck
- **Device Control** — Shell execution, file management, Termux APIs
- **Memory** — Persistent short and long-term memory per session
- **LLM Backend** — Works with OpenAI, OpenRouter, or any OpenAI-compatible API

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/qwen-bit/termux-agent/main/install.sh | bash
```

## Manual Setup

```bash
git clone https://github.com/qwen-bit/termux-agent
cd termux-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python agent.py "Your goal here"
```

## Usage

```bash
# Run with a goal
python agent.py "Set up a Python web server and test it"

# Interactive mode
python agent.py --interactive

# With verbose logging
python agent.py --verbose "Organize all .txt files in ~/Downloads"

# Specify max iterations
python agent.py --max-steps 20 "Build a todo app in Python"
```

## Configuration

Edit `.env`:

```
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1   # or OpenRouter etc.
MODEL=gpt-4o
MAX_STEPS=15
MEMORY_ENABLED=true
```

## Skills Available

| Skill | Description |
|---|---|
| `shell` | Execute terminal commands |
| `file` | Read/write/list files |
| `web` | Fetch URLs, search web |
| `memory` | Save/recall information |
| `device` | Termux device control (vibrate, notify, etc.) |
| `code` | Write and run code snippets |

## Requirements

- Python 3.8+
- pip
- Internet connection (for LLM API)
- Termux (on Android) or any Linux terminal
