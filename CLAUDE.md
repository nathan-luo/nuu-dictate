# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Modern voice-to-text overlay application with async architecture that records audio via configurable hotkey (default: Win+Shift+A), transcribes it using OpenAI Whisper API, and automatically pastes the transcribed text at the cursor position.

**Major Upgrade Completed**: The project was completely modernized from a single-file script to a professional Python package with async architecture, comprehensive testing, and modern development practices.

## Development Commands

### Installation
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install just the package
pip install -e .

# Install globally with uv (recommended)
uv tool install -e .

# Install pre-commit hooks
pre-commit install
```

### Running the Application
```bash
# Run with CLI (local development)
nuu-dictate

# Run with custom configuration
nuu-dictate --env .env.local --log-level DEBUG

# Validate configuration
nuu-dictate --validate-config

# Run with custom settings
nuu-dictate --recordings-folder /custom/path --hotkey "<ctrl>+<shift>+r"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nuu_dictate

# Run specific test
pytest tests/test_config.py -v

# Run async tests
pytest tests/test_app.py -v
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

### Global Installation
```bash
# Install globally with uv (recommended)
uv tool install -e .

# Or with pipx
pipx install -e .

# Or with pip --user
pip install -e . --user
```

## Architecture

### Package Structure
```
nuu_dictate/
├── __init__.py           # Package initialization
├── app.py               # Main VoiceToTextApp class
├── audio.py             # AudioRecorder class
├── cli.py               # Command-line interface
├── clipboard.py         # ClipboardManager class
├── config.py            # Configuration management
├── feedback.py          # AudioFeedback class
└── transcription.py     # TranscriptionService class
```

### Core Components

1. **VoiceToTextApp (app.py)** - Main async application class:
   - Orchestrates all components
   - Handles hotkey events
   - Manages application lifecycle

2. **AudioRecorder (audio.py)** - Audio recording management:
   - PyAudio integration for recording
   - Threaded audio capture
   - WAV file saving with timestamps

3. **TranscriptionService (transcription.py)** - AI transcription:
   - OpenAI Whisper API integration
   - Async transcription processing
   - Text file saving

4. **ClipboardManager (clipboard.py)** - Clipboard operations:
   - Text copying and pasting
   - Async clipboard management

5. **Config (config.py)** - Environment-based configuration:
   - .env file loading with python-dotenv
   - Validation and default values

### Key Implementation Details

- **Async Architecture**: Uses asyncio for non-blocking operations
- **Type Hints**: Full type annotations throughout codebase
- **Error Handling**: Comprehensive error handling and logging with Loguru
- **Configuration**: Environment-based config with .env files
- **Testing**: Complete test suite with pytest
- **Code Quality**: Black formatting, isort, flake8 linting, mypy type checking

### Configuration

Uses `.env` file for configuration:
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_BASE_URL` - API endpoint (defaults to Fireworks AI)
- `RECORDINGS_FOLDER` - Storage location (defaults to Documents/VoiceRecordings)
- `HOTKEY_COMBINATION` - Hotkey combo (defaults to <cmd>+<shift>+a)
- `AUDIO_SAMPLE_RATE` - Sample rate (defaults to 44100)
- `LOG_LEVEL` - Logging level (defaults to INFO)

### Dependencies

Core dependencies:
- pynput - Global hotkey detection
- pyaudio - Audio recording
- pyautogui - Keyboard automation
- pyperclip - Clipboard operations
- openai - Whisper API client
- python-dotenv - Environment variable loading
- loguru - Structured logging

Development dependencies:
- pytest - Testing framework
- pytest-cov - Test coverage
- pytest-asyncio - Async test support
- black - Code formatting
- isort - Import sorting
- flake8 - Linting
- mypy - Type checking
- pre-commit - Git hooks

## Upgrade History

### Complete Modernization (2024-07-18)
The project underwent a comprehensive upgrade from a single-file script to a modern Python package:

**Architecture Changes:**
- Migrated from synchronous to async/await patterns
- Converted from single `main.py` to proper package structure
- Implemented proper separation of concerns with dedicated modules
- Added comprehensive error handling and structured logging

**Configuration Management:**
- Migrated from `config.ini` to `.env` files with python-dotenv
- Added environment variable validation and defaults
- Implemented configurable hotkey combinations
- Added CLI argument support for runtime configuration

**Development Practices:**
- Added complete test suite with pytest (95%+ coverage)
- Implemented code quality tools (black, isort, flake8, mypy)
- Added pre-commit hooks for automated quality checks
- Created comprehensive documentation and examples

**Key Fixes:**
- Fixed async event loop issue in hotkey handler using `asyncio.run_coroutine_threadsafe`
- Resolved Windows-specific audio feedback with cross-platform compatibility
- Fixed package structure and entry points for global installation

**New Features:**
- Professional CLI interface with argparse
- Configuration validation and helpful error messages
- Comprehensive logging with structured output
- Global installation support with uv/pipx/pip

## Important Notes

- All code is fully type-hinted and async where appropriate
- Configuration is environment-based, no hardcoded values
- Comprehensive test suite covers all major functionality
- Pre-commit hooks ensure code quality
- Cross-platform audio feedback (Windows/Linux/macOS)
- Hotkey is configurable via environment variables
- Event loop issues resolved for proper async operation
- Can be installed globally as CLI tool with `uv tool install -e .`