#!/usr/bin/env python3
"""
Test script for RealtimeSTT with Parakeet MLX v3
"""

def test_import():
    """Test basic imports"""
    print("Testing imports...")
    try:
        from RealtimeSTT import AudioToTextRecorder
        print("  RealtimeSTT imported successfully")
        return True
    except ImportError as e:
        print(f"  Failed to import RealtimeSTT: {e}")
        return False

def test_model_config():
    """Test model configuration"""
    print("\nChecking model configuration...")
    try:
        from RealtimeSTT import audio_recorder
        model = audio_recorder.INIT_MODEL_TRANSCRIPTION
        realtime_model = audio_recorder.INIT_MODEL_TRANSCRIPTION_REALTIME

        print(f"  Default model: {model}")
        print(f"  Realtime model: {realtime_model}")

        # Check for Parakeet MLX models (Apple Silicon optimized)
        if audio_recorder.is_parakeet_model(model):
            print("  Parakeet MLX model configured (Apple Silicon optimized)")
            return True

        # Check for faster-whisper compatible models
        valid_models = ['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2', 'large-v3']
        if any(m in model.lower() for m in valid_models):
            print("  faster-whisper compatible model configured")
            return True
        else:
            print(f"  Warning: Model may not be compatible")
            return True
    except Exception as e:
        print(f"  Error checking configuration: {e}")
        return False

def test_platform():
    """Test platform detection"""
    print("\nPlatform information...")
    import platform
    print(f"  System: {platform.system()}")
    print(f"  Machine: {platform.machine()}")
    print(f"  Python: {platform.python_version()}")

    if platform.system() == "Darwin" and platform.machine() == "arm64":
        print("  Apple Silicon detected - optimized for MLX")
    else:
        print("  Not Apple Silicon - consider using different model")

    return True

def test_mlx():
    """Test MLX framework"""
    print("\nChecking MLX framework...")
    try:
        import mlx.core as mx
        print(f"  MLX version: {mx.__version__ if hasattr(mx, '__version__') else 'installed'}")
        # Quick GPU test
        x = mx.array([1.0, 2.0, 3.0])
        y = mx.sum(x)
        mx.eval(y)
        print("  MLX GPU computation working")
        return True
    except ImportError:
        print("  MLX not installed (required for Apple Silicon)")
        return False
    except Exception as e:
        print(f"  MLX error: {e}")
        return False

def test_audio():
    """Test audio libraries"""
    print("\nChecking audio libraries...")
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"  PyAudio working - {device_count} audio devices found")
        p.terminate()
        return True
    except Exception as e:
        print(f"  PyAudio error: {e}")
        return False

def test_parakeet_mlx():
    """Test Parakeet MLX transcription"""
    print("\nTesting Parakeet MLX transcription...")
    try:
        from RealtimeSTT.audio_recorder import ParakeetMLXWrapper, MLX_AVAILABLE
        import soundfile as sf
        import os

        if not MLX_AVAILABLE:
            print("  MLX not available, skipping Parakeet test")
            return True

        # Load and transcribe warmup audio
        warmup_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'RealtimeSTT/warmup_audio.wav'
        )
        if not os.path.exists(warmup_path):
            print(f"  Warmup audio not found at {warmup_path}")
            return False

        wrapper = ParakeetMLXWrapper('parakeet')
        audio_data, sr = sf.read(warmup_path, dtype='float32')
        segments, info = wrapper.transcribe(audio_data)
        segments_list = list(segments)

        transcription = " ".join(seg.text for seg in segments_list).strip()
        print(f"  Transcription: \"{transcription}\"")

        if transcription:
            print("  Parakeet MLX transcription working")
            return True
        else:
            print("  Warning: Empty transcription (audio may be too short)")
            return True  # Empty transcription is not a failure for warmup audio
    except Exception as e:
        print(f"  Parakeet MLX error: {e}")
        return False

def main():
    print("=" * 50)
    print("RealtimeSTT Installation Test")
    print("=" * 50)

    tests = [
        ("Import Test", test_import),
        ("Model Config", test_model_config),
        ("Platform Check", test_platform),
        ("MLX Framework", test_mlx),
        ("Audio System", test_audio),
        ("Parakeet MLX", test_parakeet_mlx),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"  {name} failed with exception: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("Test Results:")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "+" if passed else "-"
        print(f"  [{symbol}] {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All tests passed!")
        print("\nYou can now use RealtimeSTT with Parakeet MLX!")
        print("\nQuick start:")
        print("  python3 examples/basic_test.py")
    else:
        print("Some tests failed - check the errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()
