"""Tests for CLI functionality."""

import sys
from unittest.mock import patch, Mock

import pytest

from nuu_dictate.cli import create_parser, main


class TestCLI:
    """Test command-line interface functionality."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        
        assert parser.prog == "nuu-dictate"
        assert "Voice-to-text overlay" in parser.description
    
    def test_parser_version(self):
        """Test version argument."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--version'])
    
    def test_parser_env_arg(self):
        """Test environment file argument."""
        parser = create_parser()
        args = parser.parse_args(['--env', '.env.local'])
        
        assert args.env == '.env.local'
    
    def test_parser_log_level_arg(self):
        """Test log level argument."""
        parser = create_parser()
        args = parser.parse_args(['--log-level', 'DEBUG'])
        
        assert args.log_level == 'DEBUG'
    
    def test_parser_recordings_folder_arg(self):
        """Test recordings folder argument."""
        parser = create_parser()
        args = parser.parse_args(['--recordings-folder', '/custom/path'])
        
        assert args.recordings_folder == '/custom/path'
    
    def test_parser_hotkey_arg(self):
        """Test hotkey argument."""
        parser = create_parser()
        args = parser.parse_args(['--hotkey', '<ctrl>+<shift>+r'])
        
        assert args.hotkey == '<ctrl>+<shift>+r'
    
    def test_parser_validate_config_arg(self):
        """Test validate config argument."""
        parser = create_parser()
        args = parser.parse_args(['--validate-config'])
        
        assert args.validate_config is True
    
    def test_main_validate_config_success(self):
        """Test main with validate config flag (success)."""
        test_args = ['nuu-dictate', '--validate-config']
        
        with patch.object(sys, 'argv', test_args):
            with patch('nuu_dictate.cli.Config') as mock_config:
                mock_config_instance = Mock()
                mock_config_instance.validate.return_value = True
                mock_config.return_value = mock_config_instance
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 0
    
    def test_main_validate_config_failure(self):
        """Test main with validate config flag (failure)."""
        test_args = ['nuu-dictate', '--validate-config']
        
        with patch.object(sys, 'argv', test_args):
            with patch('nuu_dictate.cli.Config') as mock_config:
                mock_config_instance = Mock()
                mock_config_instance.validate.return_value = False
                mock_config.return_value = mock_config_instance
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
    
    def test_main_keyboard_interrupt(self):
        """Test main with keyboard interrupt."""
        test_args = ['nuu-dictate']
        
        with patch.object(sys, 'argv', test_args):
            with patch('nuu_dictate.cli.Config') as mock_config:
                with patch('nuu_dictate.cli.VoiceToTextApp') as mock_app:
                    mock_app_instance = Mock()
                    mock_app_instance.run.side_effect = KeyboardInterrupt()
                    mock_app.return_value = mock_app_instance
                    
                    with patch('asyncio.run') as mock_run:
                        mock_run.side_effect = KeyboardInterrupt()
                        
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        
                        assert exc_info.value.code == 0
    
    def test_main_exception(self):
        """Test main with general exception."""
        test_args = ['nuu-dictate']
        
        with patch.object(sys, 'argv', test_args):
            with patch('nuu_dictate.cli.Config') as mock_config:
                mock_config.side_effect = Exception("Test error")
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1