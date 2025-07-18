"""Audio feedback for NUU Dictate."""

import asyncio
import sys
import platform
from typing import Optional
from loguru import logger

if platform.system() == "Windows":
    import winsound


class AudioFeedback:
    """Manager for audio feedback during recording."""
    
    @staticmethod
    async def play_start_sound() -> None:
        """Play sound when recording starts."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, AudioFeedback._play_start_sound_sync)
            logger.debug("Start sound played")
        except Exception as e:
            logger.error(f"Failed to play start sound: {e}")
    
    @staticmethod
    async def play_stop_sound() -> None:
        """Play sound when recording stops."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, AudioFeedback._play_stop_sound_sync)
            logger.debug("Stop sound played")
        except Exception as e:
            logger.error(f"Failed to play stop sound: {e}")
    
    @staticmethod
    def _play_start_sound_sync() -> None:
        """Play start sound synchronously."""
        if platform.system() == "Windows":
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except Exception:
                AudioFeedback._fallback_beep()
        else:
            AudioFeedback._fallback_beep()
    
    @staticmethod
    def _play_stop_sound_sync() -> None:
        """Play stop sound synchronously."""
        if platform.system() == "Windows":
            try:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            except Exception:
                AudioFeedback._fallback_beep()
        else:
            AudioFeedback._fallback_beep()
    
    @staticmethod
    def _fallback_beep() -> None:
        """Fallback beep using terminal bell."""
        try:
            print('\a', end='', flush=True)
        except Exception:
            pass  # Silent fallback