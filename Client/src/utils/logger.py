import logging
import sys
from pathlib import Path

from ..config.config_manager import ConfigManager


class Logger:
    """Logger utility for the application."""
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the logger with the configured log level."""
        config = ConfigManager()
        log_level = getattr(logging, config.settings.log_level.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logger
        self._logger = logging.getLogger("maas_client")
        self._logger.setLevel(log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(logs_dir / "client.log")
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance."""
        return self._logger


def get_logger() -> logging.Logger:
    """Get the logger instance."""
    return Logger().logger 