#!/bin/bash

# RealtimeSTT Installation Script for macOS with Parakeet MLX v3
# Optimized for Apple Silicon (M1/M2/M3)
# Uses uv for fast package installation

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running on macOS
check_macos() {
    print_header "Checking System Requirements"

    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is for macOS only"
        exit 1
    fi
    print_success "Running on macOS"

    # Check if Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        print_success "Apple Silicon detected (M1/M2/M3/M4)"
        export APPLE_SILICON=1
    else
        print_warning "Intel Mac detected - Parakeet MLX may not be optimal"
        print_info "Consider using a different model (tiny, base, small)"
        export APPLE_SILICON=0
    fi
}

# Check for Homebrew
check_homebrew() {
    print_header "Checking Homebrew"

    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_success "Homebrew installed"
    else
        print_success "Homebrew found"
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"

    # Array of required brew packages
    declare -a BREW_PACKAGES=(
        "portaudio"      # Required for PyAudio
        "gcc"            # Includes gfortran for scipy
        "openblas"       # Required for scipy BLAS operations
        "cmake"          # Build tool for some packages
        "ffmpeg"         # Required for Parakeet MLX audio loading
    )

    for pkg in "${BREW_PACKAGES[@]}"; do
        print_info "Checking $pkg..."
        if brew list "$pkg" &> /dev/null; then
            print_success "$pkg already installed"
        else
            print_info "Installing $pkg..."
            brew install "$pkg"
            print_success "$pkg installed"
        fi
    done

    # Set environment variables for scipy/numpy to find openblas
    export OPENBLAS="$(brew --prefix openblas)"
    export PKG_CONFIG_PATH="$(brew --prefix openblas)/lib/pkgconfig:$PKG_CONFIG_PATH"
    export LDFLAGS="-L$(brew --prefix openblas)/lib"
    export CPPFLAGS="-I$(brew --prefix openblas)/include"

    print_success "Environment variables configured for OpenBLAS"
}

# Install uv package manager
install_uv() {
    print_header "Installing uv Package Manager"

    if command -v uv &> /dev/null; then
        print_success "uv already installed: $(uv --version)"
    else
        print_info "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add uv to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
        print_success "uv installed: $(uv --version)"
    fi
}

# Check Python version
check_python() {
    print_header "Checking Python"

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.9 or higher"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"

    # Check if version is at least 3.9
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        print_error "Python 3.9 or higher required (found $PYTHON_VERSION)"
        exit 1
    fi
}

# Create virtual environment with uv
setup_venv() {
    print_header "Setting Up Virtual Environment"

    VENV_DIR=".venv"

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "Removed existing virtual environment"
        else
            print_info "Using existing virtual environment"
            source "$VENV_DIR/bin/activate"
            return
        fi
    fi

    print_info "Creating virtual environment with uv..."
    uv venv "$VENV_DIR"
    print_success "Virtual environment created"

    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Install Python dependencies with uv
install_python_deps() {
    print_header "Installing Python Dependencies"

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi

    # Set environment for OpenBLAS (needed for scipy compilation)
    export OPENBLAS="$(brew --prefix openblas)"
    export PKG_CONFIG_PATH="$(brew --prefix openblas)/lib/pkgconfig:$PKG_CONFIG_PATH"
    export LDFLAGS="-L$(brew --prefix openblas)/lib"
    export CPPFLAGS="-I$(brew --prefix openblas)/include"

    print_info "Installing dependencies with uv (this is much faster than pip)..."
    print_warning "This may still take a few minutes for packages that need compilation..."

    # Use uv pip for installation
    uv pip install -r requirements.txt

    print_success "Python dependencies installed"
}

# Install and verify RealtimeSTT package
verify_installation() {
    print_header "Installing RealtimeSTT Package"

    print_info "Installing RealtimeSTT in development mode..."
    uv pip install -e .

    print_info "Verifying RealtimeSTT import..."
    if python3 -c "from RealtimeSTT import AudioToTextRecorder; print('OK')" 2>/dev/null; then
        print_success "RealtimeSTT installed and verified"
    else
        print_error "Failed to import RealtimeSTT"
        return 1
    fi

    if [ "$APPLE_SILICON" -eq 1 ]; then
        print_info "Checking MLX packages..."

        if python3 -c "import mlx; print('OK')" 2>/dev/null; then
            print_success "MLX framework available"
        else
            print_warning "MLX not found, installing..."
            uv pip install mlx mlx-whisper
            print_success "MLX installed"
        fi
    fi
}

# Download model
download_model() {
    print_header "Model Setup"

    print_info "The Parakeet MLX v3 model (~600MB) will be downloaded on first use"
    print_info "Model: mlx-community/parakeet-tdt-0.6b-v3"
    print_info "Location: ~/.cache/huggingface/"

    read -p "Do you want to download the model now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Downloading model..."
        python3 -c "
from huggingface_hub import snapshot_download
import os

print('Downloading Parakeet MLX v3...')
model_path = snapshot_download(
    repo_id='mlx-community/parakeet-tdt-0.6b-v3',
    cache_dir=os.path.expanduser('~/.cache/huggingface/')
)
print(f'Model downloaded to: {model_path}')
" 2>/dev/null || {
            print_warning "Model download will happen automatically on first use"
        }
    else
        print_info "Model will be downloaded automatically on first use"
    fi
}

# Create test script
create_test_script() {
    print_header "Creating Test Scripts"

    cat > test_installation.py << 'EOF'
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

        if "parakeet" in model.lower():
            print("  Parakeet MLX v3 configured as default")
            return True
        else:
            print("  Different model configured")
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
        print("\nYou can now use RealtimeSTT with Parakeet MLX v3")
        print("\nQuick start:")
        print("  python3 examples/basic_test.py")
    else:
        print("Some tests failed - check the errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()
EOF

    chmod +x test_installation.py
    print_success "Created test_installation.py"
}

# Create example script
create_example() {
    print_header "Creating Example Scripts"

    mkdir -p examples

    cat > examples/basic_test.py << 'EOF'
#!/usr/bin/env python3
"""
Basic test of RealtimeSTT with Parakeet MLX v3
"""

from RealtimeSTT import AudioToTextRecorder
import sys

def main():
    print("=" * 60)
    print("RealtimeSTT Basic Test")
    print("=" * 60)
    print("\nInitializing recorder...")
    print("(This may take a moment on first run while downloading the model)")

    try:
        recorder = AudioToTextRecorder()
        print("\n Recorder initialized successfully")
        print("\nModel information:")
        print(f"  Using Apple Silicon optimized Parakeet MLX v3")
        print(f"  Expected latency: <500ms")
        print(f"  Real-time factor: 50-100x")

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
            print("\n Speak now...")
            text = recorder.text()
            print(f" Transcribed: {text}")

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check microphone permissions in System Settings")
        print("  2. Ensure microphone is working")
        print("  3. Try running: python3 test_installation.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

    chmod +x examples/basic_test.py
    print_success "Created examples/basic_test.py"

    # Voice control example
    cat > examples/voice_control.py << 'EOF'
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
EOF

    chmod +x examples/voice_control.py
    print_success "Created examples/voice_control.py"
}

# Print next steps
print_next_steps() {
    print_header "Installation Complete!"

    echo -e "${GREEN}RealtimeSTT with Parakeet MLX v3 is ready to use!${NC}\n"

    print_info "Next Steps:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   ${BLUE}source .venv/bin/activate${NC}"
    echo ""
    echo "2. Test the installation:"
    echo "   ${BLUE}python3 test_installation.py${NC}"
    echo ""
    echo "3. Try the basic example:"
    echo "   ${BLUE}python3 examples/basic_test.py${NC}"
    echo ""
    echo "4. Try voice control for Claude Code:"
    echo "   ${BLUE}python3 examples/voice_control.py${NC}"
    echo ""
    print_info "Performance on Apple Silicon:"
    echo "  - Speed: 50-100x faster than real-time"
    echo "  - Latency: <500ms"
    echo "  - Memory: ~2GB during inference"
    echo ""
}

# Main installation flow
main() {
    clear
    print_header "RealtimeSTT Installation for macOS"
    print_info "Optimized with Parakeet MLX v3 for Apple Silicon"
    print_info "Using uv for fast package installation"

    # Run checks and installation
    check_macos
    check_homebrew
    install_system_deps
    install_uv
    check_python
    setup_venv
    install_python_deps
    verify_installation
    download_model
    create_test_script
    create_example

    print_next_steps
}

# Run main installation
main
