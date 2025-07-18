"""Main application class for NUU Dictate."""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional
from pynput import keyboard
from loguru import logger

from .config import Config
from .audio import AudioRecorder
from .transcription import TranscriptionService
from .clipboard import ClipboardManager
from .feedback import AudioFeedback


class VoiceToTextApp:
    """Main voice-to-text application."""
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize the application.
        
        Args:
            config: Application configuration. If None, creates default config.
        """
        self.config = config or Config()
        self.audio_recorder = AudioRecorder(self.config)
        self.transcription_service = TranscriptionService(self.config)
        self.clipboard_manager = ClipboardManager()
        self.audio_feedback = AudioFeedback()
        
        self.hotkey_listener: Optional[keyboard.GlobalHotKeys] = None
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Setup logging
        logger.remove()
        logger.add(
            sys.stderr,
            level=self.config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>"
        )
        
        logger.info("NUU Dictate initialized")
    
    def setup_hotkey_listener(self) -> None:
        """Set up global hotkey listener."""
        try:
            hotkey_dict = {self.config.hotkey_combination: self._on_hotkey}
            self.hotkey_listener = keyboard.GlobalHotKeys(hotkey_dict)
            self.hotkey_listener.start()
            logger.info(f"Hotkey listener started: {self.config.hotkey_combination}")
        except Exception as e:
            logger.error(f"Failed to setup hotkey listener: {e}")
            raise
    
    def _on_hotkey(self) -> None:
        """Handle hotkey press."""
        try:
            if self.audio_recorder.recording:
                logger.info("Stopping recording...")
                if self.loop and self.loop.is_running():
                    asyncio.run_coroutine_threadsafe(self._stop_recording(), self.loop)
            else:
                logger.info("Starting recording...")
                if self.loop and self.loop.is_running():
                    asyncio.run_coroutine_threadsafe(self._start_recording(), self.loop)
        except Exception as e:
            logger.error(f"Error handling hotkey: {e}")
    
    async def _start_recording(self) -> None:
        """Start recording with audio feedback."""
        try:
            await self.audio_feedback.play_start_sound()
            success = self.audio_recorder.start_recording()
            if not success:
                logger.error("Failed to start recording")
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
    
    async def _stop_recording(self) -> None:
        """Stop recording and process the audio."""
        try:
            await self.audio_feedback.play_stop_sound()
            audio_path = self.audio_recorder.stop_recording()
            
            if audio_path:
                await self._process_recording(audio_path)
            else:
                logger.warning("No audio recorded")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
    
    async def _process_recording(self, audio_path: Path) -> None:
        """Process recorded audio file.
        
        Args:
            audio_path: Path to recorded audio file.
        """
        try:
            logger.info(f"Processing recording: {audio_path}")
            
            # Transcribe audio
            transcript = await self.transcription_service.transcribe_audio(audio_path)
            
            if transcript:
                # Copy to clipboard and paste
                await self.clipboard_manager.copy_and_paste(transcript)
                logger.info("Transcription completed and pasted")
            else:
                logger.warning("No transcription received")
                
        except Exception as e:
            logger.error(f"Error processing recording: {e}")
    
    async def run(self) -> None:
        """Run the application."""
        try:
            # Store event loop reference for hotkey handler
            self.loop = asyncio.get_running_loop()
            
            # Validate configuration
            if not self.config.validate():
                logger.error("Configuration validation failed")
                return
            
            # Setup hotkey listener
            self.setup_hotkey_listener()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self.running = True
            logger.info("Voice-to-text overlay started")
            logger.info(f"Press {self.config.hotkey_combination} to record")
            logger.info("Press Ctrl+C to exit")
            
            # Main loop
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.cleanup()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            logger.info("Cleaning up resources...")
            
            if self.hotkey_listener:
                self.hotkey_listener.stop()
                logger.info("Hotkey listener stopped")
            
            if self.audio_recorder:
                self.audio_recorder.cleanup()
                logger.info("Audio recorder cleaned up")
            
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def stop(self) -> None:
        """Stop the application."""
        self.running = False