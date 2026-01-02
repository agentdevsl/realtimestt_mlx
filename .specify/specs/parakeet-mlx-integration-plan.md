# Parakeet MLX v3 Integration Plan for RealtimeSTT

## Objective
Configure RealtimeSTT to use Parakeet MLX (v3) as the default ASR model for optimal performance on MacBook M1 Pro.

## Background

### What is Parakeet MLX?
Parakeet MLX is a port of NVIDIA's Parakeet ASR models optimized for Apple Silicon using Apple's MLX framework. It provides ultra-fast, low-latency transcription on M1/M2/M3 Macs.

**Performance on Apple Silicon:**
- M3: 53 seconds for 1hr 1min 28sec audio (65MB)
- Average processing time: ~0.5 seconds
- Significantly faster than standard Whisper implementations on Mac

**Model Details:**
- Latest version: `mlx-community/parakeet-tdt-0.6b-v3`
- Parameter count: 0.6B
- Memory requirement: Minimum 2GB unified memory
- Compatible with: M1/M2/M3 Macs

## Implementation Strategy: Minimal Changes Approach

### Option 1: Model Path Override (RECOMMENDED - Minimal Changes)
Simply change the default model string from `"tiny"` to the Parakeet MLX model path.

**Changes Required:**
1. Update `INIT_MODEL_TRANSCRIPTION` constant
2. Update `INIT_MODEL_TRANSCRIPTION_REALTIME` constant
3. Update requirements to include `parakeet-mlx` library

**Advantages:**
- Minimal code changes (2 lines)
- Backwards compatible
- Users can still override with other models

**Limitations:**
- Relies on faster_whisper supporting MLX models OR requires parakeet-mlx to be compatible with the existing pipeline

### Option 2: Add MLX Backend Support (More Comprehensive)
Implement MLX as an alternative backend alongside faster_whisper.

**Changes Required:**
1. Add MLX backend detection
2. Implement conditional model loading
3. Add configuration parameter for backend selection
4. Update model initialization logic

**Advantages:**
- More robust solution
- Better error handling
- Explicit backend selection

**Limitations:**
- More code changes
- Requires testing both backends

## Recommended Implementation: Hybrid Approach

For truly minimal changes while ensuring functionality, we'll:

1. **Install parakeet-mlx library** alongside existing dependencies
2. **Update default model constants** to use Parakeet MLX v3
3. **Add platform detection** to automatically use Parakeet MLX on macOS with Apple Silicon
4. **Maintain backward compatibility** by keeping faster_whisper as fallback

## Step-by-Step Implementation Plan

### Step 1: Update Requirements
**File:** `requirements.txt`

Add parakeet-mlx dependency:
```
parakeet-mlx>=0.1.0
```

### Step 2: Update Model Constants
**File:** `RealtimeSTT/audio_recorder.py`

Update lines 68-69:
```python
# Old:
INIT_MODEL_TRANSCRIPTION = "tiny"
INIT_MODEL_TRANSCRIPTION_REALTIME = "tiny"

# New:
INIT_MODEL_TRANSCRIPTION = "mlx-community/parakeet-tdt-0.6b-v3"
INIT_MODEL_TRANSCRIPTION_REALTIME = "mlx-community/parakeet-tdt-0.6b-v3"
```

### Step 3: Add Platform Detection (Optional but Recommended)
Add conditional default based on platform:
```python
import platform

# Detect Apple Silicon
IS_APPLE_SILICON = (
    platform.system() == "Darwin" and
    platform.machine() == "arm64"
)

if IS_APPLE_SILICON:
    INIT_MODEL_TRANSCRIPTION = "mlx-community/parakeet-tdt-0.6b-v3"
    INIT_MODEL_TRANSCRIPTION_REALTIME = "mlx-community/parakeet-tdt-0.6b-v3"
else:
    INIT_MODEL_TRANSCRIPTION = "tiny"
    INIT_MODEL_TRANSCRIPTION_REALTIME = "tiny"
```

### Step 4: Update Documentation
**File:** `README.md`

Add note about Apple Silicon optimization:
- Mention Parakeet MLX as default for Apple Silicon
- Document performance benefits
- Provide instructions for reverting to other models if needed

## Installation Guide

### For End Users (MacBook M1 Pro)

```bash
# Clone repository
git clone <repo-url>
cd RealtimeSTT

# Install with MLX support
pip install -r requirements.txt

# Verify installation
python -c "import parakeet_mlx; print('Parakeet MLX installed successfully')"
```

### Model Download
The model will be automatically downloaded from Hugging Face on first use:
- Model: `mlx-community/parakeet-tdt-0.6b-v3`
- Size: ~600MB
- Location: `~/.cache/huggingface/`

### Testing the Installation

```python
from RealtimeSTT import AudioToTextRecorder

# Will use Parakeet MLX v3 by default on Apple Silicon
recorder = AudioToTextRecorder()

# Test transcription
print("Listening... (speak now)")
text = recorder.text()
print(f"Transcribed: {text}")
```

## Verification Steps

1. **Check platform detection:**
   ```python
   import platform
   print(f"System: {platform.system()}")
   print(f"Machine: {platform.machine()}")
   ```

2. **Verify model loading:**
   - Check logs for model initialization
   - Confirm Parakeet MLX is being used
   - Monitor memory usage (~2GB expected)

3. **Performance benchmark:**
   - Test transcription speed
   - Compare with previous tiny model
   - Expected: 50-100x real-time speedup

## Rollback Plan

If issues occur, users can override the default:

```python
# Use original tiny model
recorder = AudioToTextRecorder(
    model="tiny",
    realtime_model_type="tiny"
)

# Or use any other model
recorder = AudioToTextRecorder(
    model="base",
    realtime_model_type="base"
)
```

## Dependencies

### Required Libraries
- `mlx` - Apple's machine learning framework
- `parakeet-mlx` - Parakeet ASR implementation for MLX
- Existing: `faster-whisper`, `torch`, etc.

### System Requirements
- macOS 12.0 or later
- Apple Silicon (M1/M2/M3)
- Minimum 8GB RAM (16GB recommended)
- ~1GB free disk space for model

## Expected Outcomes

### Performance Improvements
- **Speed:** 50-100x faster than real-time
- **Latency:** <1 second for typical utterances
- **Memory:** ~2GB during inference
- **CPU/GPU:** Efficient use of Neural Engine

### Compatibility
- ✅ MacBook M1 Pro
- ✅ All M1/M2/M3 Macs
- ❌ Intel Macs (will need fallback)
- ❌ Windows/Linux (will need fallback)

## Testing Checklist

- [ ] Install parakeet-mlx library
- [ ] Update model constants
- [ ] Test on M1 Mac
- [ ] Verify model downloads correctly
- [ ] Benchmark transcription speed
- [ ] Test real-time transcription
- [ ] Verify wake word detection still works
- [ ] Test with different audio inputs
- [ ] Document any issues or edge cases

## References

- [GitHub: senstella/parakeet-mlx](https://github.com/senstella/parakeet-mlx) - Original MLX port
- [GitHub: EliFuzz/parakeet-mlx](https://github.com/EliFuzz/parakeet-mlx) - Enhanced implementation
- [Speech-to-text with Parakeet 0.6b v2](https://mikeesto.com/posts/parakeet-tdt-06b-v2/) - Performance analysis
- [mlx-whisper PyPI](https://pypi.org/project/mlx-whisper/) - MLX Whisper package

## Timeline

- **Step 1-2:** Update requirements and constants (5 minutes)
- **Step 3:** Add platform detection (10 minutes)
- **Step 4:** Update documentation (15 minutes)
- **Testing:** Full verification (30 minutes)

**Total Estimated Time:** 1 hour

## Notes

- This approach maintains full backward compatibility
- Users on non-Apple Silicon platforms will need to override the default
- Consider adding an environment variable for model selection
- Future: Could implement automatic backend selection based on available hardware
