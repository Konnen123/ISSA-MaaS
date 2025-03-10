import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    api_base_url: str = Field(..., env="API_BASE_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    session_file: str = Field(".session", env="SESSION_FILE")


class ConfigManager:
    """Manages application configuration and settings."""
    _instance: Optional["ConfigManager"] = None
    _settings: Optional[Settings] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the configuration by loading environment variables."""
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        
        # Create settings from environment variables
        self._settings = Settings(
            api_base_url=os.getenv("API_BASE_URL", "http://localhost:5000/api/v1"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            session_file=os.getenv("SESSION_FILE", ".session")
        )

    @property
    def settings(self) -> Settings:
        """Get the application settings."""
        return self._settings 