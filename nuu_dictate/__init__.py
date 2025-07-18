"""
NUU Dictate - Voice-to-text overlay application.

A modern voice-to-text overlay that records audio via hotkey,
transcribes it using OpenAI Whisper API, and automatically
pastes the transcribed text at the cursor position.
"""

__version__ = "0.1.0"
__author__ = "NUU Dictate Team"

from .app import VoiceToTextApp
from .config import Config
from .audio import AudioRecorder
from .transcription import TranscriptionService

__all__ = ["VoiceToTextApp", "Config", "AudioRecorder", "TranscriptionService"]