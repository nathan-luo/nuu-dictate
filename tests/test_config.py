"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from nuu_dictate.config import Config


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.openai_base_url == "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1"
        assert config.audio_sample_rate == 44100
        assert config.audio_channels == 1
        assert config.audio_chunk_size == 1024
        assert config.hotkey_combination == "<cmd>+<shift>+a"
        assert config.log_level == "INFO"
    
    def test_env_file_loading(self):
        """Test loading configuration from .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("OPENAI_API_KEY=test_key\n")
            f.write("AUDIO_SAMPLE_RATE=48000\n")
            f.write("LOG_LEVEL=DEBUG\n")
            env_file = f.name
        
        try:
            config = Config(env_file=env_file)
            
            assert config.openai_api_key == "test_key"
            assert config.audio_sample_rate == 48000
            assert config.log_level == "DEBUG"
        finally:
            os.unlink(env_file)
    
    def test_recordings_folder_creation(self):
        """Test recordings folder creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recordings_path = Path(temp_dir) / "recordings"
            
            with patch.dict(os.environ, {"RECORDINGS_FOLDER": str(recordings_path)}):
                config = Config()
                assert config.recordings_folder == recordings_path
                assert recordings_path.exists()
    
    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            config = Config()
            assert not config.validate()
    
    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test_key",
                "RECORDINGS_FOLDER": temp_dir
            }):
                config = Config()
                assert config.validate()