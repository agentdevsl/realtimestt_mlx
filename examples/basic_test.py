#!/usr/bin/env python3
"""
Basic test of RealtimeSTT with Parakeet MLX
"""

from RealtimeSTT import AudioToTextRecorder
from RealtimeSTT.audio_recorder import MLX_AVAILABLE, is_parakeet_model, INIT_MODEL_TRANSCRIPTION
import sys

def main():
    print("=" * 60)
    print("RealtimeSTT Basic Test")
    print("=" * 60)
    print("\nInitializing recorder...")
    print("(This may take a moment on first run while downloading the model)")

    try:
        recorder = AudioToTextRecorder()
        print("\nRecorder initialized successfully!")
        print("\nModel information:")
        if MLX_AVAILABLE and is_parakeet_model(INIT_MODEL_TRANSCRIPTION):
            print("  Using Parakeet MLX (Apple Silicon optimized)")
            print("  Hardware acceleration via Metal GPU")
        else:
            print("  Using faster-whisper")
        print("  For Whisper models: AudioToTextRecorder(model='large-v3')")

        print("\n" + "=" * 60)
        print("Ready to transcribe!")
        print("=" * 60)
        print("\nInstructions:")
        print("  - Wait for 'Speak now' prompt")
        print("  - Speak clearly into your microphone")
        print("  - Stop speaking when done")
        print("  - Press Ctrl+C to exit")
        print("\n" + "=" * 60)

        while True:
            print("\nSpeak now...")
            text = recorder.text()
            print(f"Transcribed: {text}")

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Check microphone permissions in System Settings")
        print("  2. Ensure microphone is working")
        print("  3. Try running: python3 test_installation.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
