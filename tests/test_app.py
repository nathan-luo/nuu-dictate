"""Tests for main application."""

import tempfile
from unittest.mock import Mock, patch, AsyncMock

import pytest

from nuu_dictate.app import VoiceToTextApp
from nuu_dictate.config import Config


class TestVoiceToTextApp:
    """Test main application functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict('os.environ', {
                'RECORDINGS_FOLDER': temp_dir,
                'OPENAI_API_KEY': 'test_key'
            }):
                yield Config()
    
    @pytest.fixture
    def app(self, config):
        """Create application instance."""
        with patch('nuu_dictate.app.AudioRecorder') as mock_audio:
            with patch('nuu_dictate.app.TranscriptionService') as mock_transcription:
                with patch('nuu_dictate.app.ClipboardManager') as mock_clipboard:
                    with patch('nuu_dictate.app.AudioFeedback') as mock_feedback:
                        app = VoiceToTextApp(config)
                        yield app
    
    def test_initialization(self, app):
        """Test application initialization."""
        assert app.config is not None
        assert app.audio_recorder is not None
        assert app.transcription_service is not None
        assert app.clipboard_manager is not None
        assert app.audio_feedback is not None
        assert app.hotkey_listener is None
        assert app.running is False
    
    def test_setup_hotkey_listener(self, app):
        """Test hotkey listener setup."""
        with patch('nuu_dictate.app.keyboard.GlobalHotKeys') as mock_hotkeys:
            mock_listener = Mock()
            mock_hotkeys.return_value = mock_listener
            
            app.setup_hotkey_listener()
            
            assert app.hotkey_listener == mock_listener
            mock_listener.start.assert_called_once()
    
    def test_on_hotkey_start_recording(self, app):
        """Test hotkey handler for starting recording."""
        app.audio_recorder.recording = False
        
        with patch('asyncio.create_task') as mock_create_task:
            app._on_hotkey()
            
            mock_create_task.assert_called_once()
    
    def test_on_hotkey_stop_recording(self, app):
        """Test hotkey handler for stopping recording."""
        app.audio_recorder.recording = True
        
        with patch('asyncio.create_task') as mock_create_task:
            app._on_hotkey()
            
            mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_recording(self, app):
        """Test starting recording."""
        app.audio_feedback.play_start_sound = AsyncMock()
        app.audio_recorder.start_recording.return_value = True
        
        await app._start_recording()
        
        app.audio_feedback.play_start_sound.assert_called_once()
        app.audio_recorder.start_recording.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_recording(self, app):
        """Test stopping recording."""
        from pathlib import Path
        
        app.audio_feedback.play_stop_sound = AsyncMock()
        app.audio_recorder.stop_recording.return_value = Path('/test/audio.wav')
        
        with patch.object(app, '_process_recording') as mock_process:
            await app._stop_recording()
            
            app.audio_feedback.play_stop_sound.assert_called_once()
            app.audio_recorder.stop_recording.assert_called_once()
            mock_process.assert_called_once_with(Path('/test/audio.wav'))
    
    @pytest.mark.asyncio
    async def test_process_recording(self, app):
        """Test processing recording."""
        from pathlib import Path
        
        audio_path = Path('/test/audio.wav')
        app.transcription_service.transcribe_audio = AsyncMock(return_value="transcribed text")
        app.clipboard_manager.copy_and_paste = AsyncMock(return_value=True)
        
        await app._process_recording(audio_path)
        
        app.transcription_service.transcribe_audio.assert_called_once_with(audio_path)
        app.clipboard_manager.copy_and_paste.assert_called_once_with("transcribed text")
    
    @pytest.mark.asyncio
    async def test_cleanup(self, app):
        """Test application cleanup."""
        mock_listener = Mock()
        app.hotkey_listener = mock_listener
        app.audio_recorder.cleanup = Mock()
        
        await app.cleanup()
        
        mock_listener.stop.assert_called_once()
        app.audio_recorder.cleanup.assert_called_once()
    
    def test_stop(self, app):
        """Test stopping application."""
        app.running = True
        
        app.stop()
        
        assert app.running is False