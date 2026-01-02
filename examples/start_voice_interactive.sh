#!/bin/bash
#
# Start Voice-Activated Claude Code (Interactive PTY Mode)
#
# Full interactive Claude CLI with voice input support.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
else
    echo "Error: Virtual environment not found at $PROJECT_DIR/.venv"
    echo "Run ./install_macos_mlx.sh first"
    exit 1
fi

# Run the voice control script
python3 "$SCRIPT_DIR/claude_voice_interactive.py" "$@"
