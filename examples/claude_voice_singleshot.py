#!/usr/bin/env python3
"""
Voice-activated Claude Code interface - Single-shot mode.

Each voice command runs as an independent Claude query using -p flag.
Simpler but doesn't maintain conversation context between commands.

Usage:
    python3 claude_voice_singleshot.py
"""

from RealtimeSTT import AudioToTextRecorder
import subprocess
import sys
import os
import re
import shutil

# Wake phrases that trigger Claude
WAKE_PHRASES = ["claude", "hey claude", "ok claude", "hi claude"]


def find_claude_binary() -> str:
    """Find the claude binary path."""
    locations = [
        shutil.which("claude"),
        os.path.expanduser("~/.claude/local/claude"),
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
    ]

    for loc in locations:
        if loc and os.path.isfile(loc) and os.access(loc, os.X_OK):
            return loc

    # Try to get from shell
    try:
        result = subprocess.run(
            ["zsh", "-ic", "which claude"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            path = result.stdout.strip().split()[-1]
            if os.path.isfile(path):
                return path
    except:
        pass

    return None


def extract_command(text: str) -> str | None:
    """Extract command after wake phrase."""
    text_lower = text.lower().strip()

    for phrase in WAKE_PHRASES:
        if phrase in text_lower:
            parts = text_lower.split(phrase, 1)
            if len(parts) > 1:
                cmd = parts[1].strip()
                cmd = re.sub(r'^[,\s]*(please|can you|could you|would you)\s*', '', cmd)
                if cmd:
                    return text.split(phrase)[-1].strip().lstrip(',').strip()
            return ""
    return None


def run_claude_command(claude_path: str, command: str):
    """Run a single Claude command using -p flag."""
    print(f"\n{'='*60}")
    print(f"[Voice command: {command}]")
    print('='*60)

    try:
        # Run Claude with -p for single prompt
        result = subprocess.run(
            [claude_path, "-p", command],
            text=True,
            timeout=120  # 2 minute timeout
        )
    except subprocess.TimeoutExpired:
        print("\n[Command timed out]")
    except Exception as e:
        print(f"\n[Error: {e}]")


def main():
    print("=" * 60)
    print("Voice-Activated Claude Code (Single-Shot Mode)")
    print("=" * 60)

    claude_path = find_claude_binary()
    if not claude_path:
        print("\nError: 'claude' command not found.")
        print("Install with: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    print(f"\nUsing Claude at: {claude_path}")
    print("\nInitializing voice recognition...")

    try:
        recorder = AudioToTextRecorder(
            spinner=True,
            post_speech_silence_duration=0.4,
            min_length_of_recording=0.3,
        )

        print("\nVoice control ready!")
        print("\nHow to use:")
        print('  Say "Claude" followed by your request')
        print('  Example: "Claude, what files are in this directory?"')
        print('  Say "Claude exit" or press Ctrl+C to quit')
        print("\n" + "=" * 60)

        listening_for_command = False

        while True:
            print("\nListening... (say 'Claude' to activate)")
            text = recorder.text()

            if not text.strip():
                continue

            print(f"Heard: {text}")

            # Check for exit
            if "exit" in text.lower() and "claude" in text.lower():
                print("\nExiting...")
                break

            command = extract_command(text)

            if command is not None:
                if command:
                    run_claude_command(claude_path, command)
                else:
                    print("Yes? (listening for command...)")
                    listening_for_command = True
            elif listening_for_command:
                run_claude_command(claude_path, text)
                listening_for_command = False

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
