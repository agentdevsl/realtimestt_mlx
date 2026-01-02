# Quick Start Guide

## Installation (One Command)

```bash
./install_macos_mlx.sh
```

That's it! The script handles everything automatically.

## What Gets Installed?

- ✓ System dependencies (portaudio)
- ✓ Python virtual environment
- ✓ RealtimeSTT library
- ✓ Parakeet MLX v3 model (~600MB)
- ✓ All required dependencies
- ✓ Test and example scripts

## First Test (After Installation)

```bash
# Activate virtual environment
source venv/bin/activate

# Run test
python3 test_installation.py
```

Expected output:
```
==================================================
RealtimeSTT Installation Test
==================================================
Testing imports...
✓ RealtimeSTT imported successfully

Checking model configuration...
  Default model: mlx-community/parakeet-tdt-0.6b-v3
  Realtime model: mlx-community/parakeet-tdt-0.6b-v3
✓ Parakeet MLX v3 configured as default

Platform information...
  System: Darwin
  Machine: arm64
  Python: 3.x.x
✓ Apple Silicon detected - optimized for MLX

==================================================
✓ All tests passed!
==================================================
```

## Basic Usage

### Simple Speech-to-Text

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder()

    print("Speak now...")
    text = recorder.text()
    print(f"You said: {text}")
```

### Run the Example

```bash
python3 examples/basic_test.py
```

## Voice Control for Claude Code

### Example Script

```bash
python3 examples/voice_control.py
```

### Voice Commands

Say:
- **"Claude help"** → Runs `claude help`
- **"Claude status"** → Runs `claude status`
- **"Help"** → Shows available commands
- **"Exit"** or **"Quit"** → Exits voice control

### Custom Voice Control Script

```python
from RealtimeSTT import AudioToTextRecorder
import subprocess

def execute_claude_command(text):
    if "claude" in text.lower():
        cmd = text.lower().replace("claude", "").strip()
        subprocess.run(["claude", cmd])

if __name__ == '__main__':
    recorder = AudioToTextRecorder()

    while True:
        text = recorder.text()
        print(f"Heard: {text}")
        execute_claude_command(text)
```

## Performance Tips

### For Lowest Latency (Voice Commands)

```python
recorder = AudioToTextRecorder(
    post_speech_silence_duration=0.3,  # Quick cutoff
    realtime_processing_pause=0.1,     # Fast updates
    silero_sensitivity=0.5             # Sensitive detection
)
```

### For Best Accuracy (Transcription)

```python
recorder = AudioToTextRecorder(
    post_speech_silence_duration=1.0,  # Wait for complete sentence
    silero_sensitivity=0.3             # Less noise interference
)
```

## Common Issues

### "Microphone permission denied"

1. Go to: System Settings → Privacy & Security → Microphone
2. Enable Terminal (or your IDE)
3. Restart Terminal

### "Model download failed"

```bash
# Check internet connection and try again
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('mlx-community/parakeet-tdt-0.6b-v3')
"
```

### "Import error"

```bash
# Reinstall package
source venv/bin/activate
pip install -e .
```

## Expected Performance (M1 Mac)

| Metric | Value |
|--------|-------|
| **Transcription Speed** | 50-100x real-time |
| **Latency** | <500ms |
| **Memory Usage** | ~2GB |
| **CPU Usage** | Low (uses Neural Engine) |
| **Model Size** | ~600MB |

## Next Steps

1. **Customize for your use case**
   - Adjust sensitivity settings
   - Add custom wake words
   - Integrate with your apps

2. **Explore examples**
   - `example_app/` - Complete applications
   - `examples/` - Simple examples

3. **Read full documentation**
   - `README.md` - Complete API reference
   - `INSTALL.md` - Detailed installation guide
   - `.specify/specs/` - Technical details

## Support

Need help? Check:
- `INSTALL.md` - Troubleshooting section
- GitHub Issues - Report problems
- Examples directory - More code samples

---

**Enjoy ultra-fast voice recognition on your M1 Mac! 🎤✨**
