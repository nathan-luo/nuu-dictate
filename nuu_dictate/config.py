"""Configuration management for NUU Dictate."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, env_file: Optional[str] = None) -> None:
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file. If None, uses default .env in project root.
        """
        if env_file is None:
            env_file = Path(__file__).parent.parent / ".env"
        
        if Path(env_file).exists():
            load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            logger.warning(f"No .env file found at {env_file}")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def openai_base_url(self) -> str:
        """Get OpenAI base URL."""
        return os.getenv(
            "OPENAI_BASE_URL", 
            "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1"
        )
    
    @property
    def recordings_folder(self) -> Path:
        """Get recordings folder path."""
        folder = os.getenv("RECORDINGS_FOLDER", "Documents/VoiceRecordings")
        if not os.path.isabs(folder):
            folder = Path.home() / folder
        else:
            folder = Path(folder)
        
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    @property
    def audio_sample_rate(self) -> int:
        """Get audio sample rate."""
        return int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
    
    @property
    def audio_channels(self) -> int:
        """Get audio channels."""
        return int(os.getenv("AUDIO_CHANNELS", "1"))
    
    @property
    def audio_chunk_size(self) -> int:
        """Get audio chunk size."""
        return int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
    
    @property
    def hotkey_combination(self) -> str:
        """Get hotkey combination."""
        return os.getenv("HOTKEY_COMBINATION", "<cmd>+<shift>+a")
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY is required")
            return False
        
        if not self.recordings_folder.exists():
            logger.error(f"Recordings folder does not exist: {self.recordings_folder}")
            return False
        
        logger.info("Configuration validated successfully")
        return True