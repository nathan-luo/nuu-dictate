"""Tests for clipboard functionality."""

from unittest.mock import patch, Mock

import pytest

from nuu_dictate.clipboard import ClipboardManager


class TestClipboardManager:
    """Test clipboard manager functionality."""
    
    @pytest.mark.asyncio
    async def test_copy_and_paste_success(self):
        """Test successful copy and paste operation."""
        with patch('nuu_dictate.clipboard.pyperclip.copy') as mock_copy:
            with patch('nuu_dictate.clipboard.pyautogui.hotkey') as mock_hotkey:
                result = await ClipboardManager.copy_and_paste("test text")
                
                assert result is True
                mock_copy.assert_called_once_with("test text")
                mock_hotkey.assert_called_once_with('ctrl', 'v')
    
    @pytest.mark.asyncio
    async def test_copy_and_paste_error(self):
        """Test copy and paste with error."""
        with patch('nuu_dictate.clipboard.pyperclip.copy') as mock_copy:
            mock_copy.side_effect = Exception("Clipboard error")
            
            result = await ClipboardManager.copy_and_paste("test text")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_copy_to_clipboard_success(self):
        """Test successful copy to clipboard."""
        with patch('nuu_dictate.clipboard.pyperclip.copy') as mock_copy:
            result = await ClipboardManager.copy_to_clipboard("test text")
            
            assert result is True
            mock_copy.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_copy_to_clipboard_error(self):
        """Test copy to clipboard with error."""
        with patch('nuu_dictate.clipboard.pyperclip.copy') as mock_copy:
            mock_copy.side_effect = Exception("Clipboard error")
            
            result = await ClipboardManager.copy_to_clipboard("test text")
            
            assert result is False