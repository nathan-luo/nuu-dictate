"""Command-line interface for NUU Dictate."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from . import __version__
from .app import VoiceToTextApp
from .config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="nuu-dictate",
        description="Voice-to-text overlay with hotkey activation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nuu-dictate                    # Run with default settings
  nuu-dictate --env .env.local   # Use custom environment file
  nuu-dictate --log-level DEBUG  # Enable debug logging
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--env",
        type=str,
        help="Path to environment file (default: .env in project root)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (overrides LOG_LEVEL env var)"
    )
    
    parser.add_argument(
        "--recordings-folder",
        type=str,
        help="Path to recordings folder (overrides RECORDINGS_FOLDER env var)"
    )
    
    parser.add_argument(
        "--hotkey",
        type=str,
        help="Hotkey combination (overrides HOTKEY_COMBINATION env var)"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = Config(env_file=args.env)
        
        # Override config with command-line arguments
        if args.log_level:
            import os
            os.environ["LOG_LEVEL"] = args.log_level
        
        if args.recordings_folder:
            import os
            os.environ["RECORDINGS_FOLDER"] = args.recordings_folder
        
        if args.hotkey:
            import os
            os.environ["HOTKEY_COMBINATION"] = args.hotkey
        
        # Recreate config with updated environment
        config = Config(env_file=args.env)
        
        # Validate configuration if requested
        if args.validate_config:
            if config.validate():
                logger.info("Configuration is valid")
                sys.exit(0)
            else:
                logger.error("Configuration is invalid")
                sys.exit(1)
        
        # Create and run application
        app = VoiceToTextApp(config)
        
        # Run the application
        if sys.platform == "win32":
            # On Windows, use WindowsProactorEventLoopPolicy
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(app.run())
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()