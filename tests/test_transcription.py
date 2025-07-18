"""Tests for transcription service."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from nuu_dictate.transcription import TranscriptionService
from nuu_dictate.config import Config


class TestTranscriptionService:
    """Test transcription service functionality."""
    
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
    def transcription_service(self, config):
        """Create transcription service instance."""
        with patch('nuu_dictate.transcription.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            service = TranscriptionService(config)
            yield service
    
    def test_initialization_with_api_key(self, config):
        """Test initialization with API key."""
        with patch('nuu_dictate.transcription.OpenAI') as mock_openai:
            service = TranscriptionService(config)
            
            mock_openai.assert_called_once_with(
                api_key='test_key',
                base_url=config.openai_base_url
            )
            assert service.client is not None
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=True):
            config = Config()
            service = TranscriptionService(config)
            
            assert service.client is None
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, transcription_service):
        """Test successful audio transcription."""
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'fake_audio_data')
            audio_path = Path(f.name)
        
        try:
            # Mock transcription response
            mock_transcript = Mock()
            mock_transcript.text = "Hello world"
            
            with patch.object(transcription_service, '_transcribe_sync') as mock_transcribe:
                mock_transcribe.return_value = "Hello world"
                
                with patch.object(transcription_service, '_save_transcription') as mock_save:
                    result = await transcription_service.transcribe_audio(audio_path)
                    
                    assert result == "Hello world"
                    mock_transcribe.assert_called_once_with(audio_path)
                    mock_save.assert_called_once()
        finally:
            audio_path.unlink()
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_file_not_found(self, transcription_service):
        """Test transcription with non-existent file."""
        non_existent_path = Path("/non/existent/file.wav")
        
        result = await transcription_service.transcribe_audio(non_existent_path)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_no_client(self, config):
        """Test transcription without OpenAI client."""
        service = TranscriptionService(config)
        service.client = None
        
        with tempfile.NamedTemporaryFile(suffix='.wav') as f:
            audio_path = Path(f.name)
            result = await service.transcribe_audio(audio_path)
            
            assert result is None
    
    def test_transcribe_sync_success(self, transcription_service):
        """Test synchronous transcription."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'fake_audio_data')
            audio_path = Path(f.name)
        
        try:
            mock_transcript = Mock()
            mock_transcript.text = "Transcribed text"
            transcription_service.client.audio.transcriptions.create.return_value = mock_transcript
            
            result = transcription_service._transcribe_sync(audio_path)
            
            assert result == "Transcribed text"
            transcription_service.client.audio.transcriptions.create.assert_called_once()
        finally:
            audio_path.unlink()
    
    def test_transcribe_sync_error(self, transcription_service):
        """Test synchronous transcription with error."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            audio_path = Path(f.name)
        
        try:
            transcription_service.client.audio.transcriptions.create.side_effect = Exception("API Error")
            
            result = transcription_service._transcribe_sync(audio_path)
            
            assert result is None
        finally:
            audio_path.unlink()
    
    @pytest.mark.asyncio
    async def test_save_transcription(self, transcription_service):
        """Test saving transcription to file."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            txt_path = Path(f.name)
        
        try:
            await transcription_service._save_transcription(txt_path, "Test transcription")
            
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == "Test transcription"
        finally:
            txt_path.unlink()