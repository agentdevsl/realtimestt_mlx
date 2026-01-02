# Quick Start: Voice-Activated Claude Code for macOS

Control Claude Code hands-free with voice commands on your Apple Silicon Mac.

## 1. Install (One Command)

```bash
./install_macos_mlx.sh
```

This installs everything: dependencies, Parakeet MLX v3, and voice control scripts.

## 2. Run Voice Control

```bash
./examples/start_voice_interactive.sh
```

## 3. Start Talking

| Say This | What Happens |
|----------|--------------|
| "Claude, list files" | Activates + sends command |
| "Opus, explain this code" | Activates with Opus wake word |
| "Hey Sonnet, help me" | Activates with Sonnet wake word |
| "Haiku, summarize" | Activates with Haiku wake word |
| "Claude exit" | Exits voice control |

**Keep talking** - stays active until 40 seconds of silence.

**Type simultaneously** - keyboard and voice work together.

## Wake Words

All Claude model names work as wake words:
- **Claude** / Hey Claude / Ok Claude
- **Opus** / Hey Opus / Ok Opus
- **Sonnet** / Hey Sonnet / Ok Sonnet
- **Haiku** / Hey Haiku / Ok Haiku

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Your Voice    │────▶│  Parakeet MLX v3 │────▶│ Claude Code │
│   (Microphone)  │     │  (Local on Mac)  │     │    (CLI)    │
└─────────────────┘     └──────────────────┘     └─────────────┘
         │                       │                      │
         │                       │                      │
    100% Local              Sub-second            Full Interactive
    No cloud upload          Latency                  CLI
```

## Requirements

- ✅ Apple Silicon Mac (M1/M2/M3/M4)
- ✅ macOS 12+
- ✅ Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)
- ✅ Microphone access

## Verify Installation

```bash
source .venv/bin/activate
python3 test_installation.py
```

Expected output:
```
✓ RealtimeSTT imported successfully
✓ Parakeet MLX v3 configured as default
✓ Apple Silicon detected - optimized for MLX
✓ All tests passed!
```

## Performance

| Metric | Value |
|--------|-------|
| **Transcription Speed** | 50-100x real-time |
| **Latency** | <500ms |
| **Memory** | ~2GB |
| **Model** | [Parakeet MLX v3](https://huggingface.co/mlx-community/parakeet-tdt-0.6b-v3) |

## Troubleshooting

### "Microphone permission denied"
1. System Settings → Privacy & Security → Microphone
2. Enable Terminal (or your IDE)
3. Restart Terminal

### Claude not found
```bash
npm install -g @anthropic-ai/claude-code
```

### Voice not recognized
- Speak clearly after wake word
- Check microphone in System Settings → Sound → Input
- Try: "Hey Claude" (more distinct)

## Privacy

🔒 **100% Local Processing**
- Voice never leaves your Mac
- Parakeet MLX runs entirely on-device
- Only transcribed text goes to Claude API

---

**Ready to code hands-free! 🎤**
