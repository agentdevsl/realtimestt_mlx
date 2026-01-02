#!/usr/bin/env python3
"""
Voice-activated Claude Code interface.

Usage:
    python3 claude_voice.py

Say "Hey Claude" or "Claude" followed by your command to interact.
Examples:
    "Claude, what files are in this directory?"
    "Hey Claude, explain this code"
    "Claude help me write a function"
"""

from RealtimeSTT import AudioToTextRecorder
import subprocess
import sys
import os
import re
import threading
import queue
import shutil

# Wake phrases that trigger Claude
WAKE_PHRASES = ["claude", "hey claude", "ok claude", "hi claude"]

def find_claude_binary() -> str:
    """Find the claude binary path."""
    # Check common locations
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
            path = result.stdout.strip().split()[-1]  # Handle "aliased to X" output
            if os.path.isfile(path):
                return path
    except:
        pass

    return None

# Queue for commands to send to Claude
command_queue = queue.Queue()

def extract_command(text: str) -> str | None:
    """Extract command after wake phrase."""
    text_lower = text.lower().strip()

    for phrase in WAKE_PHRASES:
        if phrase in text_lower:
            # Get everything after the wake phrase
            parts = text_lower.split(phrase, 1)
            if len(parts) > 1:
                cmd = parts[1].strip()
                # Remove common filler words at start
                cmd = re.sub(r'^[,\s]*(please|can you|could you|would you)\s*', '', cmd)
                if cmd:
                    return text.split(phrase)[-1].strip().lstrip(',').strip()
            # Wake phrase said but no command - return empty to indicate activation
            return ""
    return None


def run_claude_interactive():
    """Run Claude Code in interactive mode."""
    print("\n[Starting Claude Code...]")

    claude_path = find_claude_binary()
    if not claude_path:
        print("\nError: 'claude' command not found.")
        print("Make sure Claude Code CLI is installed.")
        print("Install with: npm install -g @anthropic-ai/claude-code")
        return

    print(f"[Using: {claude_path}]")

    try:
        # Start Claude in interactive mode
        process = subprocess.Popen(
            [claude_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Thread to read Claude's output
        def read_output():
            for line in process.stdout:
                print(line, end='', flush=True)

        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()

        # Process commands from queue
        while True:
            try:
                cmd = command_queue.get(timeout=0.5)
                if cmd == "EXIT":
                    process.stdin.write("/exit\n")
                    process.stdin.flush()
                    break
                elif cmd:
                    print(f"\n[Voice command: {cmd}]")
                    process.stdin.write(cmd + "\n")
                    process.stdin.flush()
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue

        process.wait()

    except Exception as e:
        print(f"\nError running Claude: {e}")


def main():
    print("=" * 60)
    print("Voice-Activated Claude Code")
    print("=" * 60)
    print("\nInitializing voice recognition...")
    print("(First run may take a moment to download the model)")

    try:
        # Initialize recorder with settings optimized for wake word detection
        recorder = AudioToTextRecorder(
            spinner=True,
            post_speech_silence_duration=0.4,  # Faster response
            min_length_of_recording=0.3,
        )

        print("\nVoice control ready!")
        print("\nHow to use:")
        print('  Say "Claude" followed by your request')
        print('  Example: "Claude, explain this function"')
        print('  Say "Claude exit" or press Ctrl+C to quit')
        print("\n" + "=" * 60)

        # Start Claude in background thread
        claude_thread = threading.Thread(target=run_claude_interactive, daemon=True)
        claude_thread.start()

        # Give Claude time to start
        import time
        time.sleep(2)

        listening_for_command = False

        while True:
            if not claude_thread.is_alive():
                print("\nClaude process ended. Exiting...")
                break

            print("\nListening... (say 'Claude' to activate)")
            text = recorder.text()

            if not text.strip():
                continue

            print(f"Heard: {text}")

            # Check for exit command
            if "exit" in text.lower() and "claude" in text.lower():
                print("\nExiting...")
                command_queue.put("EXIT")
                break

            # Extract command after wake phrase
            command = extract_command(text)

            if command is not None:
                if command:
                    # Full command received
                    command_queue.put(command)
                else:
                    # Just wake word, wait for command
                    print("Yes? (listening for command...)")
                    listening_for_command = True
            elif listening_for_command:
                # Previous wake word, this is the command
                command_queue.put(text)
                listening_for_command = False

        # Wait for Claude to finish
        claude_thread.join(timeout=5)

    except KeyboardInterrupt:
        print("\n\nExiting...")
        command_queue.put("EXIT")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
