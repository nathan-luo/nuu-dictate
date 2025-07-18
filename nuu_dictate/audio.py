"""Audio recording functionality for NUU Dictate."""

import asyncio
import threading
import wave
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
import pyaudio
from loguru import logger

from .config import Config


class AudioRecorder:
    """Audio recording manager."""
    
    def __init__(self, config: Config) -> None:
        """Initialize audio recorder.
        
        Args:
            config: Application configuration.
        """
        self.config = config
        self.recording = False
        self.audio_frames: List[bytes] = []
        self.audio_stream: Optional[pyaudio.Stream] = None
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_format = pyaudio.paInt16
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self._print_device_info()
    
    def _print_device_info(self) -> None:
        """Print information about the default audio input device."""
        try:
            default_device = self.audio.get_default_input_device_info()
            logger.info(f"Audio input device: {default_device['name']}")
            logger.info(f"Device index: {default_device['index']}")
            logger.info(f"Max input channels: {default_device['maxInputChannels']}")
            logger.info(f"Default sample rate: {default_device['defaultSampleRate']}")
        except Exception as e:
            logger.error(f"Could not get audio device info: {e}")
    
    def start_recording(self, on_start: Optional[Callable] = None) -> bool:
        """Start audio recording.
        
        Args:
            on_start: Optional callback to execute when recording starts.
            
        Returns:
            True if recording started successfully, False otherwise.
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return False
        
        try:
            self.recording = True
            self.audio_frames = []
            
            # Execute start callback
            if on_start:
                on_start()
            
            # Start audio stream
            self.audio_stream = self.audio.open(
                format=self.audio_format,
                channels=self.config.audio_channels,
                rate=self.config.audio_sample_rate,
                input=True,
                frames_per_buffer=self.config.audio_chunk_size
            )
            
            # Start recording in separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            
            logger.info("Recording started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording = False
            return False
    
    def stop_recording(self, on_stop: Optional[Callable] = None) -> Optional[Path]:
        """Stop audio recording and save to file.
        
        Args:
            on_stop: Optional callback to execute when recording stops.
            
        Returns:
            Path to saved audio file if successful, None otherwise.
        """
        if not self.recording:
            logger.warning("No recording in progress")
            return None
        
        try:
            self.recording = False
            
            # Execute stop callback
            if on_stop:
                on_stop()
            
            # Stop audio stream
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join()
                self.recording_thread = None
            
            # Save audio file
            if self.audio_frames:
                audio_path = self._save_audio_file()
                logger.info(f"Recording stopped and saved to {audio_path}")
                return audio_path
            else:
                logger.warning("No audio data recorded")
                return None
                
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    def _record_audio(self) -> None:
        """Record audio data in a separate thread."""
        while self.recording and self.audio_stream:
            try:
                data = self.audio_stream.read(self.config.audio_chunk_size)
                self.audio_frames.append(data)
            except Exception as e:
                logger.error(f"Recording error: {e}")
                break
    
    def _save_audio_file(self) -> Path:
        """Save recorded audio frames to a WAV file.
        
        Returns:
            Path to the saved audio file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        audio_path = self.config.recordings_folder / f"{timestamp}.wav"
        
        with wave.open(str(audio_path), 'wb') as wav_file:
            wav_file.setnchannels(self.config.audio_channels)
            wav_file.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wav_file.setframerate(self.config.audio_sample_rate)
            wav_file.writeframes(b''.join(self.audio_frames))
        
        return audio_path
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self.recording:
            self.stop_recording()
        
        if self.audio:
            self.audio.terminate()
            logger.info("Audio resources cleaned up")