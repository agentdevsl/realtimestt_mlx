#!/usr/bin/env python3
"""
Voice control example for Claude Code CLI
"""

from RealtimeSTT import AudioToTextRecorder
import subprocess
import sys

def execute_command(text):
    """Execute voice commands"""
    text_lower = text.lower().strip()

    # Claude Code commands
    if "claude" in text_lower:
        # Extract command after "claude"
        cmd = text_lower.split("claude", 1)[1].strip()
        print(f"Executing: claude {cmd}")
        try:
            result = subprocess.run(
                ["claude", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
            if result.stderr:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Error executing command: {e}")

    # System commands
    elif "exit" in text_lower or "quit" in text_lower:
        print("Exiting voice control...")
        sys.exit(0)

    elif "help" in text_lower:
        print("\nVoice Commands:")
        print("  'claude [command]' - Execute Claude Code command")
        print("  'help' - Show this help")
        print("  'exit' or 'quit' - Exit voice control")

    else:
        print(f"Unknown command: {text}")
        print("Say 'help' for available commands")

def main():
    print("=" * 60)
    print("Voice Control for Claude Code CLI")
    print("=" * 60)
    print("\nInitializing voice recognition...")

    try:
        recorder = AudioToTextRecorder()
        print(" Voice control ready!")
        print("\nSay 'help' for available commands")
        print("Press Ctrl+C to exit\n")
        print("=" * 60)

        while True:
            print("\n Listening...")
            text = recorder.text()
            print(f" Heard: {text}")
            execute_command(text)

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
