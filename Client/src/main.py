#!/usr/bin/env python3
"""
MaaS Client - Mobility as a Service Client Application

This is the main entry point for the MaaS client application.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cli_manager import CliManager
from src.utils.logger import get_logger

logger = get_logger()


def main():
    """Main entry point for the application."""
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Run the CLI manager
        cli_manager = CliManager()
        cli_manager.run()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 