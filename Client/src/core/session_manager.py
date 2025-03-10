import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from ..config.config_manager import ConfigManager
from ..utils.logger import get_logger

logger = get_logger()


class SessionManager:
    """Manages user sessions and authentication state."""
    _instance = None
    _session_data: Optional[Dict[str, Any]] = None
    _session_file: Path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the session manager."""
        config = ConfigManager()
        self._session_file = Path(config.settings.session_file)
        self._load_session()

    def _load_session(self) -> None:
        """Load session data from file if it exists."""
        if self._session_file.exists():
            try:
                with open(self._session_file, 'r') as f:
                    self._session_data = json.load(f)
                logger.debug("Session loaded successfully")
            except json.JSONDecodeError:
                logger.error("Failed to decode session file")
                self._session_data = None
            except Exception as e:
                logger.error(f"Error loading session: {str(e)}")
                self._session_data = None
        else:
            self._session_data = None

    def _save_session(self) -> None:
        """Save session data to file."""
        try:
            with open(self._session_file, 'w') as f:
                json.dump(self._session_data, f)
            logger.debug("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")

    def create_session(self, session_token: str, user_data: Dict[str, Any]) -> None:
        """Create a new session with the given token and user data."""
        self._session_data = {
            'session_token': session_token,
            'user_data': user_data
        }
        self._save_session()
        logger.info("New session created")

    def get_session_token(self) -> Optional[str]:
        """Get the current session token if it exists."""
        if self._session_data and 'session_token' in self._session_data:
            return self._session_data['session_token']
        return None

    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Get the current user data if it exists."""
        if self._session_data and 'user_data' in self._session_data:
            return self._session_data['user_data']
        return None

    def clear_session(self) -> None:
        """Clear the current session."""
        self._session_data = None
        if self._session_file.exists():
            try:
                os.remove(self._session_file)
                logger.info("Session cleared")
            except Exception as e:
                logger.error(f"Error clearing session: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return self._session_data is not None and 'session_token' in self._session_data 