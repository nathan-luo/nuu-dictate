"""Clipboard operations for NUU Dictate."""

import asyncio
import pyperclip
import pyautogui
from loguru import logger


class ClipboardManager:
    """Manager for clipboard operations and text pasting."""
    
    @staticmethod
    async def copy_and_paste(text: str) -> bool:
        """Copy text to clipboard and paste it.
        
        Args:
            text: Text to copy and paste.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info(f"Copying text to clipboard: {text[:50]}...")
            
            # Run clipboard operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, pyperclip.copy, text)
            await loop.run_in_executor(None, pyautogui.hotkey, 'ctrl', 'v')
            
            logger.info("Text copied to clipboard and pasted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy and paste text: {e}")
            return False
    
    @staticmethod
    async def copy_to_clipboard(text: str) -> bool:
        """Copy text to clipboard only.
        
        Args:
            text: Text to copy.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info(f"Copying text to clipboard: {text[:50]}...")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, pyperclip.copy, text)
            
            logger.info("Text copied to clipboard")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy text to clipboard: {e}")
            return False