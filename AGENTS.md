# RealtimeSTT with Parakeet MLX - Project Guidelines

## Project Overview

RealtimeSTT is a speech-to-text library optimized for Apple Silicon (M1/M2/M3/M4) Macs using Parakeet MLX for hardware-accelerated transcription via Metal.

## Key Features

- **Parakeet MLX**: Native Apple Silicon acceleration using MLX framework
- **Real-time transcription**: Sub-500ms latency speech-to-text
- **Voice Activity Detection (VAD)**: Automatic speech detection
- **Wake word detection**: Supports Porcupine and OpenWakeWord
- **Drop-in replacement**: Compatible with faster-whisper API

## Architecture

### Core Components

```
RealtimeSTT/
├── audio_recorder.py     # Main audio recording and transcription engine
├── safepipe.py          # Safe multiprocessing pipe wrapper
└── warmup_audio.wav     # Model warmup audio file
```

### Key Classes

1. **AudioToTextRecorder**: Main class for recording and transcription
2. **ParakeetMLXWrapper**: Adapter that wraps Parakeet MLX to match faster_whisper API
3. **TranscriptionWorker**: Multiprocessing worker for transcription

## Parakeet MLX Integration

### Model Selection

The system automatically selects Parakeet MLX on Apple Silicon:

```python
if platform.system() == 'Darwin' and platform.machine() == 'arm64' and MLX_AVAILABLE:
    INIT_MODEL_TRANSCRIPTION = "parakeet"
else:
    INIT_MODEL_TRANSCRIPTION = "small"  # Falls back to faster-whisper
```

### Supported Parakeet Models

| Model Name | HuggingFace ID |
|------------|----------------|
| `parakeet` | `mlx-community/parakeet-tdt-0.6b-v2` |
| `parakeet-tdt` | `mlx-community/parakeet-tdt-0.6b-v2` |
| `parakeet-tdt-0.6b` | `mlx-community/parakeet-tdt-0.6b-v2` |

### ParakeetMLXWrapper API

The wrapper adapts Parakeet MLX to match the faster_whisper interface:

```python
from RealtimeSTT.audio_recorder import ParakeetMLXWrapper

wrapper = ParakeetMLXWrapper('parakeet')
segments, info = wrapper.transcribe(audio_data)

# segments: Iterator of ParakeetSegment objects (text, start, end)
# info: ParakeetTranscriptionInfo (language, duration, etc.)
```

## Development Guidelines

### Python Standards

- Python 3.10+ required
- Use type hints for all public functions
- Use numpy arrays for audio data (float32, 16kHz mono)
- Use soundfile for audio I/O
- Use tempfile for temporary audio storage

### Key Dependencies

| Package | Purpose |
|---------|---------|
| `parakeet-mlx` | MLX-based ASR for Apple Silicon |
| `mlx` | Apple's ML framework for Metal |
| `faster-whisper` | Fallback for non-Apple Silicon |
| `soundfile` | Audio file I/O |
| `pyaudio` | Real-time audio capture |
| `webrtcvad` | Voice activity detection |

### System Requirements

- macOS (for MLX support)
- Apple Silicon (M1/M2/M3/M4) for optimal performance
- FFmpeg (required by Parakeet for audio loading)
- PortAudio (required by PyAudio)

## Testing

### Run Installation Test

```bash
python3 test_installation.py
```

Expected output:
- Import Test: PASS
- Model Config: PASS (Parakeet MLX model configured)
- Platform Check: PASS (Apple Silicon detected)
- MLX Framework: PASS
- Audio System: PASS
- Parakeet MLX: PASS (transcription working)

### Manual Transcription Test

```python
from RealtimeSTT.audio_recorder import ParakeetMLXWrapper
import soundfile as sf

wrapper = ParakeetMLXWrapper('parakeet')
audio_data, sr = sf.read('audio.wav', dtype='float32')
segments, info = wrapper.transcribe(audio_data)
print(" ".join(seg.text for seg in segments))
```

## Common Issues

### FFmpeg Not Found

```
RuntimeError: FFmpeg is not installed or not in your PATH.
```

Solution: `brew install ffmpeg`

### MLX Not Available

The system will fall back to faster-whisper on non-Apple Silicon or if MLX is not installed.

### Empty Transcription

Very short audio clips or non-speech audio may return empty transcriptions. This is expected behavior.

## File Locations

| File | Purpose |
|------|---------|
| `RealtimeSTT/audio_recorder.py` | Main engine with Parakeet MLX integration |
| `test_installation.py` | Installation verification tests |
| `install_macos_mlx.sh` | macOS installation script |
| `examples/basic_test.py` | Basic usage example |
| `examples/voice_control.py` | Voice control example |

## Quick Start

```bash
# Install
./install_macos_mlx.sh

# Test
python3 test_installation.py

# Run basic example
python3 examples/basic_test.py
```

## Usage

```python
from RealtimeSTT import AudioToTextRecorder

# Uses Parakeet MLX by default on Apple Silicon
recorder = AudioToTextRecorder()

# Or explicitly specify the model
recorder = AudioToTextRecorder(model="parakeet")

# Transcribe
while True:
    print("Speak now...")
    text = recorder.text()
    print(f"Transcribed: {text}")
```
