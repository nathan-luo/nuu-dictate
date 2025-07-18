"""Tests for audio recording functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from nuu_dictate.audio import AudioRecorder
from nuu_dictate.config import Config


class TestAudioRecorder:
    """Test audio recording functionality."""
    
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
    def audio_recorder(self, config):
        """Create audio recorder instance."""
        with patch('nuu_dictate.audio.pyaudio.PyAudio') as mock_pyaudio:
            mock_audio = Mock()
            mock_pyaudio.return_value = mock_audio
            mock_audio.get_default_input_device_info.return_value = {
                'name': 'Test Device',
                'index': 0,
                'maxInputChannels': 2,
                'defaultSampleRate': 44100
            }
            
            recorder = AudioRecorder(config)
            yield recorder
    
    def test_initialization(self, audio_recorder):
        """Test audio recorder initialization."""
        assert not audio_recorder.recording
        assert audio_recorder.audio_frames == []
        assert audio_recorder.audio_stream is None
        assert audio_recorder.recording_thread is None
    
    def test_start_recording(self, audio_recorder):
        """Test starting recording."""
        mock_stream = Mock()
        audio_recorder.audio.open.return_value = mock_stream
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            result = audio_recorder.start_recording()
            
            assert result is True
            assert audio_recorder.recording is True
            assert audio_recorder.audio_stream == mock_stream
            mock_thread_instance.start.assert_called_once()
    
    def test_start_recording_already_recording(self, audio_recorder):
        """Test starting recording when already recording."""
        audio_recorder.recording = True
        
        result = audio_recorder.start_recording()
        
        assert result is False
    
    def test_stop_recording(self, audio_recorder):
        """Test stopping recording."""
        # Setup recording state
        audio_recorder.recording = True
        audio_recorder.audio_frames = [b'test_data']
        
        mock_stream = Mock()
        mock_thread = Mock()
        audio_recorder.audio_stream = mock_stream
        audio_recorder.recording_thread = mock_thread
        
        with patch.object(audio_recorder, '_save_audio_file') as mock_save:
            mock_save.return_value = Path('/test/path.wav')
            
            result = audio_recorder.stop_recording()
            
            assert result == Path('/test/path.wav')
            assert audio_recorder.recording is False
            mock_stream.stop_stream.assert_called_once()
            mock_stream.close.assert_called_once()
            mock_thread.join.assert_called_once()
    
    def test_stop_recording_no_recording(self, audio_recorder):
        """Test stopping recording when not recording."""
        result = audio_recorder.stop_recording()
        
        assert result is None
    
    def test_save_audio_file(self, audio_recorder):
        """Test saving audio file."""
        audio_recorder.audio_frames = [b'test_data_1', b'test_data_2']
        
        with patch('wave.open') as mock_wave_open:
            mock_wav_file = Mock()
            mock_wave_open.return_value.__enter__.return_value = mock_wav_file
            
            audio_recorder.audio.get_sample_size.return_value = 2
            
            result = audio_recorder._save_audio_file()
            
            assert result.suffix == '.wav'
            mock_wav_file.setnchannels.assert_called_once_with(1)
            mock_wav_file.setsampwidth.assert_called_once_with(2)
            mock_wav_file.setframerate.assert_called_once_with(44100)
            mock_wav_file.writeframes.assert_called_once_with(b'test_data_1test_data_2')
    
    def test_cleanup(self, audio_recorder):
        """Test cleanup of resources."""
        audio_recorder.recording = True
        mock_stream = Mock()
        audio_recorder.audio_stream = mock_stream
        
        with patch.object(audio_recorder, 'stop_recording') as mock_stop:
            audio_recorder.cleanup()
            
            mock_stop.assert_called_once()
            audio_recorder.audio.terminate.assert_called_once()