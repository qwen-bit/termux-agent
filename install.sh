#!/usr/bin/env bash
# TermuxAgent — one-liner installer
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_GITHUB_USER/termux-agent/main/install.sh | bash

set -e

REPO="https://github.com/YOUR_GITHUB_USER/termux-agent"
INSTALL_DIR="$HOME/termux-agent"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║       TermuxAgent Installer          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Detect environment ──────────────────────────────────────────────────────
IS_TERMUX=false
if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    IS_TERMUX=true
    echo "[+] Termux environment detected"
else
    echo "[+] Standard Linux environment detected"
fi

# ── Install system dependencies ─────────────────────────────────────────────
echo "[+] Installing system dependencies..."
if $IS_TERMUX; then
    pkg update -y -q
    pkg install -y python git curl 2>/dev/null || true
else
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip git curl 2>/dev/null || true
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip git curl 2>/dev/null || true
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip git curl 2>/dev/null || true
    elif command -v brew &>/dev/null; then
        brew install python git curl 2>/dev/null || true
    fi
fi

# ── Clone or update repo ─────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[+] Updating existing installation..."
    git -C "$INSTALL_DIR" pull --quiet
else
    echo "[+] Cloning TermuxAgent..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# ── Install Python dependencies ──────────────────────────────────────────────
echo "[+] Installing Python dependencies..."
pip install -q -r requirements.txt

# ── Set up .env ──────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  ACTION REQUIRED: Add your API key to .env           ║"
    echo "║                                                      ║"
    echo "║  nano $INSTALL_DIR/.env          ║"
    echo "║                                                      ║"
    echo "║  Set OPENAI_API_KEY=your_key_here                    ║"
    echo "╚══════════════════════════════════════════════════════╝"
else
    echo "[+] .env already configured"
fi

# ── Create launcher alias ────────────────────────────────────────────────────
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

ALIAS_LINE="alias agent='python3 $INSTALL_DIR/agent.py'"
if ! grep -q "alias agent=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# TermuxAgent" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "[+] Added 'agent' alias to $SHELL_RC"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     TermuxAgent installed!           ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Usage:"
echo "  source $SHELL_RC"
echo "  agent \"Your goal here\""
echo "  agent --interactive"
echo "  agent --help"
echo ""
echo "Direct:"
echo "  python3 $INSTALL_DIR/agent.py \"Your goal\""
echo ""
