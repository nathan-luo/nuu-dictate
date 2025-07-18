"""Transcription service for NUU Dictate."""

import asyncio
from pathlib import Path
from typing import Optional
from openai import OpenAI
from loguru import logger

from .config import Config


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper."""
    
    def __init__(self, config: Config) -> None:
        """Initialize transcription service.
        
        Args:
            config: Application configuration.
        """
        self.config = config
        self.client: Optional[OpenAI] = None
        
        if config.openai_api_key:
            self.client = OpenAI(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url
            )
            logger.info("OpenAI client initialized")
        else:
            logger.error("OpenAI API key not configured")
    
    async def transcribe_audio(self, audio_path: Path) -> Optional[str]:
        """Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file to transcribe.
            
        Returns:
            Transcribed text if successful, None otherwise.
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                None, self._transcribe_sync, audio_path
            )
            
            if transcript:
                # Save transcription to text file
                txt_path = audio_path.with_suffix('.txt')
                await self._save_transcription(txt_path, transcript)
                logger.info(f"Transcription saved to {txt_path}")
                return transcript
            else:
                logger.warning("No transcription received")
                return None
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def _transcribe_sync(self, audio_path: Path) -> Optional[str]:
        """Synchronous transcription helper.
        
        Args:
            audio_path: Path to audio file to transcribe.
            
        Returns:
            Transcribed text if successful, None otherwise.
        """
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-v3-turbo",
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            logger.error(f"Synchronous transcription failed: {e}")
            return None
    
    async def _save_transcription(self, txt_path: Path, transcript: str) -> None:
        """Save transcription to text file.
        
        Args:
            txt_path: Path to save transcription.
            transcript: Transcribed text.
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._write_text_file, txt_path, transcript
            )
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
    
    def _write_text_file(self, txt_path: Path, transcript: str) -> None:
        """Write transcription to text file (sync helper).
        
        Args:
            txt_path: Path to save transcription.
            transcript: Transcribed text.
        """
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(transcript)