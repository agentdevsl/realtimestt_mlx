#!/usr/bin/env python3
"""
Voice-activated Claude Code interface - Interactive mode with PTY.

Uses a pseudo-terminal to give Claude a proper interactive terminal,
allowing full CLI rendering while also accepting voice commands.

Usage:
    python3 claude_voice_interactive.py
"""

from RealtimeSTT import AudioToTextRecorder
import subprocess
import sys
import os
import re
import shutil
import pty
import select
import threading
import queue
import termios
import tty
import signal

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


def reset_terminal():
    """Reset terminal to sane state."""
    subprocess.run(["stty", "sane"], check=False)


class ClaudeInteractiveSession:
    """Manages an interactive Claude session with PTY."""

    def __init__(self, claude_path: str):
        self.claude_path = claude_path
        self.master_fd = None
        self.pid = None
        self.running = False
        self.command_queue = queue.Queue()

    def start(self):
        """Start Claude in a PTY."""
        # Fork a child process with a PTY
        self.pid, self.master_fd = pty.fork()

        if self.pid == 0:
            # Child process - exec Claude
            os.execv(self.claude_path, [self.claude_path])
        else:
            # Parent process
            self.running = True

            # Start threads for I/O
            self.output_thread = threading.Thread(target=self._read_output, daemon=True)
            self.output_thread.start()

            self.input_thread = threading.Thread(target=self._process_commands, daemon=True)
            self.input_thread.start()

            # Also allow keyboard input
            self.keyboard_thread = threading.Thread(target=self._read_keyboard, daemon=True)
            self.keyboard_thread.start()

    def _read_output(self):
        """Read and display output from Claude."""
        while self.running:
            try:
                r, _, _ = select.select([self.master_fd], [], [], 0.1)
                if r:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    else:
                        # EOF - Claude exited
                        self.running = False
                        break
            except OSError:
                self.running = False
                break

    def _read_keyboard(self):
        """Read keyboard input and forward to Claude."""
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Set terminal to raw mode for character-by-character input
            tty.setraw(sys.stdin.fileno())

            while self.running:
                r, _, _ = select.select([sys.stdin], [], [], 0.1)
                if r:
                    char = sys.stdin.read(1)
                    if char:
                        os.write(self.master_fd, char.encode())
        except:
            pass
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _process_commands(self):
        """Process voice commands from the queue."""
        import time
        while self.running:
            try:
                cmd = self.command_queue.get(timeout=0.5)
                if cmd == "EXIT":
                    # Send /exit to Claude
                    os.write(self.master_fd, b"/exit\n")
                    break
                elif cmd:
                    # Send the command character by character for reliability
                    for char in cmd:
                        os.write(self.master_fd, char.encode())
                        time.sleep(0.01)  # Small delay between characters
                    # Send Enter key (carriage return)
                    time.sleep(0.05)
                    os.write(self.master_fd, b"\r")
            except queue.Empty:
                continue

    def send_command(self, command: str):
        """Queue a voice command to send to Claude."""
        self.command_queue.put(command)

    def stop(self):
        """Stop the Claude session."""
        self.running = False
        self.command_queue.put("EXIT")
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, 0)
            except:
                pass


def main():
    print("=" * 60)
    print("Voice-Activated Claude Code (Interactive PTY Mode)")
    print("=" * 60)

    claude_path = find_claude_binary()
    if not claude_path:
        print("\nError: 'claude' command not found.")
        print("Install with: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    print(f"\nUsing Claude at: {claude_path}")
    print("\nInitializing voice recognition...")

    session = None
    old_settings = None

    try:
        # Save terminal settings before any modifications
        old_settings = termios.tcgetattr(sys.stdin)

        recorder = AudioToTextRecorder(
            spinner=True,
            post_speech_silence_duration=0.4,
            min_length_of_recording=0.3,
        )

        print("\nVoice control ready!")
        print("\nHow to use:")
        print('  - Type normally to interact with Claude')
        print('  - Say "Claude" followed by your request for voice input')
        print('  - Say "Claude exit" or press Ctrl+C to quit')
        print("\n" + "=" * 60)

        # Start Claude interactive session
        session = ClaudeInteractiveSession(claude_path)
        session.start()

        # Give Claude time to initialize
        import time
        time.sleep(1)

        listening_for_command = False

        while session.running:
            # Non-blocking voice check
            text = recorder.text()

            if not text.strip():
                continue

            # Restore terminal briefly to print
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print(f"\n[Voice heard: {text}]")

            # Check for exit
            if "exit" in text.lower() and "claude" in text.lower():
                print("\n[Voice: Exiting...]")
                session.stop()
                break

            command = extract_command(text)

            if command is not None:
                if command:
                    print(f"[Voice command: {command}]")
                    session.send_command(command)
                else:
                    print("[Listening for command...]")
                    listening_for_command = True
            elif listening_for_command:
                print(f"[Voice command: {text}]")
                session.send_command(text)
                listening_for_command = False

    except KeyboardInterrupt:
        print("\n\n[Exiting...]")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if session:
            session.stop()
        # Restore terminal settings
        if old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass
        # Reset terminal to sane state
        reset_terminal()


if __name__ == '__main__':
    main()
