# TermuxAgent 🤖

A powerful autonomous AI agent that runs in the terminal / Termux on Android. Give it a goal — it plans, acts, reviews, and iterates until done. **Uses 100% free AI models — no credit card required.**

## Features

- **Strategic Planner** — Breaks goals into actionable step-by-step plans
- **Skill System** — Pluggable skills: shell, file, web, device, memory, code
- **Self-Reviewer** — Reviews progress every 5 steps and replans if stuck
- **Device Control** — Shell execution, file management, Termux APIs (notify, vibrate, clipboard, TTS)
- **Memory** — Persistent short and long-term memory across sessions
- **Free LLM Backend** — Defaults to OpenRouter free models (no credit card needed)

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
nano .env   # Add your free API key (see below)
python agent.py "Your goal here"
```

## Free API Key Setup

1. Sign up at **[openrouter.ai](https://openrouter.ai)** — free, no credit card
2. Go to **[openrouter.ai/keys](https://openrouter.ai/keys)** and create a key
3. Paste it into your `.env` file:

```env
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL=google/gemma-3-27b-it:free
```

### Free Models Available

| Model | Notes |
|---|---|
| `google/gemma-3-27b-it:free` | **Default** — Smart, fast, free |
| `deepseek/deepseek-r1:free` | Best reasoning |
| `meta-llama/llama-3.3-70b-instruct:free` | Large & capable |
| `mistralai/mistral-7b-instruct:free` | Lightweight |
| `qwen/qwen3-235b-a22b:free` | Massive model |

## Usage

```bash
# Run with a goal
python agent.py "Set up a Python web server and test it"

# Interactive mode (prompt for goals in a loop)
python agent.py --interactive

# Verbose output
python agent.py --verbose "Organize all .txt files in ~/Downloads"

# Auto-approve all shell commands (use carefully)
python agent.py --auto-approve "Install and configure git"

# Limit steps
python agent.py --max-steps 10 "Build a todo app in Python"

# List all available skills/tools
python agent.py --list-skills
```

## Configuration (`.env`)

```env
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL=google/gemma-3-27b-it:free
MAX_STEPS=20
MEMORY_ENABLED=true
VERBOSE=false
AUTO_APPROVE_SHELL=false
TERMUX_API=false
```

## Skills Available

| Skill | Tools | Description |
|---|---|---|
| `shell` | `shell_run` | Execute terminal commands |
| `file` | `file_read`, `file_write`, `file_list`, `file_delete` | Read/write/list files |
| `web` | `web_fetch`, `web_search` | Fetch URLs, search DuckDuckGo |
| `memory` | `memory_save`, `memory_recall`, `memory_list` | Persistent key-value memory |
| `device` | `device_notify`, `device_vibrate`, `device_tts`, `device_battery`… | Termux device control |
| `code` | `code_run_python`, `code_run_bash` | Write and run code snippets |

## Requirements

- Python 3.8+
- pip
- Internet connection
- Termux (Android) or any Linux terminal
- A free OpenRouter API key

## Termux-specific setup

```bash
pkg install python git termux-api
termux-setup-storage
```

Then set `TERMUX_API=true` in `.env` to enable device notifications, vibration, TTS, etc.
