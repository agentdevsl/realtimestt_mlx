# Installation Guide for RealtimeSTT with Parakeet MLX v3

## Quick Installation (macOS Apple Silicon)

For M1/M2/M3 Macs, use the automated installation script:

```bash
./install_macos_mlx.sh
```

This script will:
1. ✓ Check system requirements (macOS, Apple Silicon)
2. ✓ Install Homebrew (if needed)
3. ✓ Install portaudio via Homebrew
4. ✓ Create Python virtual environment
5. ✓ Install all dependencies including Parakeet MLX v3
6. ✓ Download the model (~600MB)
7. ✓ Create test and example scripts
8. ✓ Verify installation

## Manual Installation

If you prefer to install manually:

### Step 1: Install System Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install portaudio
brew install portaudio
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install RealtimeSTT Package

```bash
pip install -e .
```

### Step 5: Verify Installation

```bash
python3 -c "from RealtimeSTT import AudioToTextRecorder; print('Success!')"
```

## First Run

On first run, the Parakeet MLX v3 model will be automatically downloaded:

- **Model**: `mlx-community/parakeet-tdt-0.6b-v3`
- **Size**: ~600MB
- **Location**: `~/.cache/huggingface/`

## Testing

### Quick Test

```bash
python3 test_installation.py
```

### Basic Speech-to-Text Test

```bash
python3 examples/basic_test.py
```

### Voice Control for Claude Code

```bash
python3 examples/voice_control.py
```

## System Requirements

### macOS (Apple Silicon - Recommended)
- **OS**: macOS 12.0 or later
- **Hardware**: M1/M2/M3 Mac
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: ~1GB free space
- **Python**: 3.8 or higher

### macOS (Intel)
⚠️ Parakeet MLX is optimized for Apple Silicon. Intel Macs should use:
```python
recorder = AudioToTextRecorder(
    model="tiny",  # or "base", "small"
    realtime_model_type="tiny"
)
```

## Microphone Permissions

On macOS, you'll need to grant microphone permissions:

1. System Settings → Privacy & Security → Microphone
2. Enable for Terminal or your Python IDE

## Performance Expectations

### Apple Silicon (M1 Pro)
- **Speed**: 50-100x faster than real-time
- **Latency**: <500ms
- **Memory**: ~2GB during inference
- **Perfect for**: Voice control, real-time commands

### Example Performance
- **1 hour audio**: Transcribes in ~60 seconds
- **Voice command**: Responds in <500ms
- **Continuous listening**: Low CPU usage

## Troubleshooting

### Model Download Issues

If the model fails to download:

```bash
# Manually download the model
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('mlx-community/parakeet-tdt-0.6b-v3')
"
```

### Microphone Not Working

```bash
# Check microphone access
python3 -c "
import pyaudio
p = pyaudio.PyAudio()
print(f'Available devices: {p.get_device_count()}')
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i)['name'])
"
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e .

# Or install as package
pip install .
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Advanced Configuration

### Using Different Models

```python
from RealtimeSTT import AudioToTextRecorder

# Use Whisper tiny model instead
recorder = AudioToTextRecorder(
    model="tiny",
    realtime_model_type="tiny"
)

# Use larger Whisper model
recorder = AudioToTextRecorder(
    model="base",  # or "small", "medium", "large"
    realtime_model_type="base"
)
```

### Custom Model Path

```python
# Use custom model
recorder = AudioToTextRecorder(
    model="/path/to/custom/model",
    realtime_model_type="/path/to/custom/model"
)
```

### Performance Tuning

```python
# Optimize for lower latency
recorder = AudioToTextRecorder(
    post_speech_silence_duration=0.3,  # Faster cutoff
    realtime_processing_pause=0.1,     # More responsive
    silero_sensitivity=0.5             # More sensitive VAD
)

# Optimize for accuracy
recorder = AudioToTextRecorder(
    post_speech_silence_duration=1.0,  # More patience
    silero_sensitivity=0.3             # Less sensitive VAD
)
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove cached models (optional)
rm -rf ~/.cache/huggingface/
```

## Next Steps

1. **Read the documentation**:
   - [Integration Plan](.specify/specs/parakeet-mlx-integration-plan.md)
   - [Changes Summary](.specify/specs/CHANGES_SUMMARY.md)

2. **Try the examples**:
   - `examples/basic_test.py` - Basic speech-to-text
   - `examples/voice_control.py` - Voice control for Claude Code

3. **Build your application**:
   - Check the main README.md for API documentation
   - See example_app/ for more complex examples

## Support

- **Issues**: Check existing issues or open a new one
- **Documentation**: See README.md and .specify/specs/
- **Examples**: See examples/ directory

## License

MIT License - See LICENSE file for details
