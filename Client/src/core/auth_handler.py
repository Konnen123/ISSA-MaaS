from typing import Dict, Any, Optional, Tuple, Union

from rich.console import Console

from ..utils.error_handler import handle_error, AuthenticationError
from ..utils.logger import get_logger
from .api_client import ApiClient
from .session_manager import SessionManager

logger = get_logger()
console = Console()


class AuthHandler:
    """Handles user authentication operations."""
    _instance = None
    _api_client: ApiClient = None
    _session_manager: SessionManager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthHandler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the authentication handler."""
        self._api_client = ApiClient()
        self._session_manager = SessionManager()
        logger.debug("Authentication handler initialized")

    @handle_error
    def login(self, email: str, password: str) -> bool:
        """Login with the given credentials."""
        if self._session_manager.is_authenticated():
            logger.warning("User is already logged in")
            console.print("[yellow]Warning:[/yellow] You are already logged in. Please logout first.")
            return False

        response = self._api_client.login(email, password)
        if response and 'session_token' in response:
            session_token = response['session_token']
            # Store user data (in a real app, we would get this from the API)
            user_data = {'email': email}
            self._session_manager.create_session(session_token, user_data)
            logger.info(f"User {email} logged in successfully")
            console.print(f"[green]Success:[/green] Logged in as {email}")
            return True
        return False

    @handle_error
    def register(self, user_data: Dict[str, Any]) -> bool:
        """Register a new user with the given data."""
        response = self._api_client.register(user_data)
        if response and 'message' in response:
            logger.info(f"User {user_data.get('email')} registered successfully")
            console.print(f"[green]Success:[/green] {response['message']}")
            return True
        return False

    @handle_error
    def logout(self) -> bool:
        """Logout the current user."""
        if not self._session_manager.is_authenticated():
            logger.warning("No user is logged in")
            console.print("[yellow]Warning:[/yellow] No user is logged in.")
            return False

        self._api_client.logout()
        self._session_manager.clear_session()
        logger.info("User logged out successfully")
        console.print("[green]Success:[/green] Logged out successfully")
        return True

    @handle_error
    def check_auth(self) -> bool:
        """Check if the user is authenticated."""
        return self._session_manager.is_authenticated()

    @handle_error
    def require_auth(self) -> None:
        """Require authentication to proceed."""
        if not self.check_auth():
            logger.warning("Authentication required but user is not logged in")
            raise AuthenticationError("You must be logged in to perform this action")

    @handle_error
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user data if authenticated."""
        return self._session_manager.get_user_data() 