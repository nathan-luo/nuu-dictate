# NUU Dictate

A modern voice-to-text overlay application that records audio via hotkey, transcribes it using OpenAI Whisper API, and automatically pastes the transcribed text at the cursor position.

## Features

- **🎯 Hotkey Activation**: Win+Shift+A to start/stop recording (configurable)
- **🔊 Audio Feedback**: System sounds for recording start/stop
- **📁 Smart Storage**: Saves recordings and transcriptions with timestamps
- **🤖 AI Transcription**: OpenAI Whisper API integration
- **📋 Auto-paste**: Copies text to clipboard and pastes at cursor
- **⚡ Async Architecture**: Modern async/await patterns for responsiveness
- **🔧 Configurable**: Environment-based configuration with .env files
- **📊 Comprehensive Logging**: Structured logging with Loguru
- **🧪 Fully Tested**: Complete test suite with pytest

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/your-username/nuu-dictate.git
cd nuu-dictate

# Install with development dependencies
pip install -e ".[dev]"

# Or install just the package
pip install -e .
```

### 2. Configure

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Run

```bash
# Run the application
nuu-dictate

# Or with custom configuration
nuu-dictate --env .env.local --log-level DEBUG
```

## Installation

### Prerequisites

- **Python 3.10+**
- **OpenAI API key**
- **Audio system**: PulseAudio/ALSA (Linux) or DirectSound (Windows)

### System Dependencies

#### Linux/Ubuntu
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

#### macOS
```bash
brew install portaudio
```

#### Windows
No additional system dependencies required.

### Python Package
```bash
# Install from source
git clone https://github.com/your-username/nuu-dictate.git
cd nuu-dictate
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1

# Application Settings
RECORDINGS_FOLDER=Documents/VoiceRecordings
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024

# Hotkey Configuration
HOTKEY_COMBINATION=<cmd>+<shift>+a

# Logging
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *required* | Your OpenAI API key |
| `OPENAI_BASE_URL` | Fireworks AI endpoint | OpenAI-compatible API base URL |
| `RECORDINGS_FOLDER` | `Documents/VoiceRecordings` | Where to save recordings |
| `AUDIO_SAMPLE_RATE` | `44100` | Audio sample rate in Hz |
| `AUDIO_CHANNELS` | `1` | Number of audio channels (1=mono, 2=stereo) |
| `AUDIO_CHUNK_SIZE` | `1024` | Audio buffer chunk size |
| `HOTKEY_COMBINATION` | `<cmd>+<shift>+a` | Hotkey combination for recording |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Usage

### Basic Usage

1. **Start the application**:
   ```bash
   nuu-dictate
   ```

2. **Record audio**:
   - Press `Win+Shift+A` (or configured hotkey) to start recording
   - Speak your text
   - Press the hotkey again to stop recording

3. **Get transcription**:
   - Audio is automatically transcribed
   - Text is copied to clipboard and pasted at cursor position
   - Recording and transcription are saved to the configured folder

4. **Exit**:
   - Press `Ctrl+C` to exit the application

### Command Line Options

```bash
# Basic usage
nuu-dictate

# Custom environment file
nuu-dictate --env .env.production

# Debug logging
nuu-dictate --log-level DEBUG

# Custom recordings folder
nuu-dictate --recordings-folder /path/to/recordings

# Custom hotkey
nuu-dictate --hotkey "<ctrl>+<shift>+r"

# Validate configuration
nuu-dictate --validate-config

# Show help
nuu-dictate --help
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-username/nuu-dictate.git
cd nuu-dictate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nuu_dictate

# Run specific test file
pytest tests/test_config.py

# Run in verbose mode
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy nuu_dictate/

# Run all quality checks
pre-commit run --all-files
```

### Project Structure

```
nuu-dictate/
├── nuu_dictate/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Main application class
│   ├── audio.py           # Audio recording functionality
│   ├── cli.py             # Command-line interface
│   ├── clipboard.py       # Clipboard operations
│   ├── config.py          # Configuration management
│   ├── feedback.py        # Audio feedback
│   └── transcription.py   # Transcription service
├── tests/                 # Test suite
├── .env.example          # Example environment file
├── .pre-commit-config.yaml # Pre-commit configuration
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## File Storage

Recordings are saved to the configured folder (default: `Documents/VoiceRecordings/`):

```
Documents/VoiceRecordings/
├── 2024-07-18_143052.wav  # Audio recording
├── 2024-07-18_143052.txt  # Transcription
├── 2024-07-18_151234.wav
├── 2024-07-18_151234.txt
└── ...
```

## Troubleshooting

### Common Issues

1. **Audio device not found**:
   - Check that your microphone is connected and working
   - Verify audio permissions for the application

2. **Hotkey not working**:
   - Make sure the hotkey combination isn't already in use
   - Try running the application as administrator (Windows)

3. **Transcription fails**:
   - Verify your OpenAI API key is correct
   - Check your internet connection
   - Ensure the audio file isn't corrupted

4. **Import errors**:
   - Make sure all dependencies are installed: `pip install -e ".[dev]"`
   - Check that you're using Python 3.10+

### Debug Mode

Run with debug logging to see detailed information:

```bash
nuu-dictate --log-level DEBUG
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and ensure all tests pass
6. Submit a pull request

## Support

- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- 📖 **Documentation**: Check the README and code comments
- 💬 **Questions**: Open a discussion on GitHub