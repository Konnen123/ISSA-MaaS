from typing import Dict, Any, Optional, List, Union

import requests
from requests.cookies import RequestsCookieJar

from ..config.config_manager import ConfigManager
from ..utils.error_handler import ApiError, AuthenticationError, handle_error
from ..utils.logger import get_logger
from .session_manager import SessionManager

logger = get_logger()


class ApiClient:
    """Client for interacting with the MaaS API."""
    _instance = None
    _base_url: str = None
    _session: requests.Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApiClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the API client."""
        config = ConfigManager()
        self._base_url = config.settings.api_base_url
        self._session = requests.Session()
        
        # Add session token to cookies if available
        session_manager = SessionManager()
        session_token = session_manager.get_session_token()
        if session_token:
            self._session.cookies.set('session_token', session_token)
        
        logger.debug(f"API client initialized with base URL: {self._base_url}")

    def _get_url(self, endpoint: str) -> str:
        """Get the full URL for the given endpoint."""
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def _update_session_token(self, cookies: RequestsCookieJar) -> None:
        """Update the session token from cookies."""
        if 'session_token' in cookies:
            session_token = cookies['session_token']
            self._session.cookies.set('session_token', session_token)
            logger.debug("Session token updated")

    @handle_error
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to the API with the given credentials."""
        url = self._get_url('/login')
        data = {'email': email, 'password': password}
        
        logger.debug(f"Sending login request to {url}")
        response = self._session.post(url, json=data)
        
        if response.status_code == 200:
            self._update_session_token(response.cookies)
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError("Invalid credentials")
        else:
            raise ApiError(f"Login failed: {response.text}", response.status_code)

    @handle_error
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user with the given data."""
        url = self._get_url('/register')
        
        logger.debug(f"Sending registration request to {url}")
        response = self._session.post(url, json=user_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise ApiError(f"Registration failed: {response.text}", response.status_code)

    @handle_error
    def get_available_cars(self) -> List[Dict[str, Any]]:
        """Get a list of available cars."""
        url = self._get_url('/cars/available')
        
        logger.debug(f"Sending request to get available cars from {url}")
        response = self._session.get(url)
        
        if response.status_code == 200:
            return response.json().get('cars', [])
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        else:
            raise ApiError(f"Failed to get available cars: {response.text}", response.status_code)

    @handle_error
    def select_car(self, car_id: int) -> bool:
        """Select a car with the given ID."""
        url = self._get_url(f'/cars/{car_id}')
        
        logger.debug(f"Sending request to select car {car_id} from {url}")
        response = self._session.patch(url)
        
        if response.status_code == 202:
            return True
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        elif response.status_code == 404:
            raise ApiError(f"Car with ID {car_id} not found", response.status_code)
        elif response.status_code == 400:
            raise ApiError(f"Car is not available: {response.text}", response.status_code)
        else:
            raise ApiError(f"Failed to select car: {response.text}", response.status_code)

    @handle_error
    def start_rent(self, car_id: int) -> bool:
        """Start renting the car with the given ID."""
        url = self._get_url(f'/cars/rental/{car_id}')
        
        logger.debug(f"Sending request to start renting car {car_id} from {url}")
        response = self._session.post(url)
        
        if response.status_code == 202:
            return True
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        elif response.status_code == 404:
            raise ApiError(f"Car with ID {car_id} not found", response.status_code)
        elif response.status_code == 400:
            raise ApiError(f"Cannot start rent: {response.text}", response.status_code)
        else:
            raise ApiError(f"Failed to start rent: {response.text}", response.status_code)

    @handle_error
    def finish_rent(self, car_id: int) -> bool:
        """Finish renting the car with the given ID."""
        url = self._get_url(f'/cars/rental/{car_id}')
        
        logger.debug(f"Sending request to finish renting car {car_id} from {url}")
        response = self._session.delete(url)
        
        if response.status_code == 202:
            return True
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        elif response.status_code == 404:
            raise ApiError(f"Car with ID {car_id} not found", response.status_code)
        elif response.status_code == 400:
            raise ApiError(f"Cannot finish rent: {response.text}", response.status_code)
        else:
            raise ApiError(f"Failed to finish rent: {response.text}", response.status_code)

    @handle_error
    def logout(self) -> None:
        """Clear the session cookies."""
        self._session.cookies.clear()
        logger.debug("Session cookies cleared")

    @handle_error
    def get_all_cars(self) -> List[Any]:
        """Get all cars from the server, regardless of availability."""
        url = self._get_url('/cars/all')
        
        logger.debug(f"Sending request to get all cars from {url}")
        response = self._session.get(url)
        
        if response.status_code == 200:
            return response.json().get('cars', [])
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        else:
            raise ApiError(f"Failed to get all cars: {response.text}", response.status_code)

    @handle_error
    def get_car_by_id(self, car_id: int) -> Optional[Any]:
        """Get a specific car by ID."""
        url = self._get_url(f'/cars/{car_id}')
        
        logger.debug(f"Sending request to get car {car_id} from {url}")
        response = self._session.get(url)
        
        if response.status_code == 200:
            return response.json().get('car')
        elif response.status_code == 401:
            raise AuthenticationError("Authentication required")
        elif response.status_code == 404:
            raise ApiError(f"Car with ID {car_id} not found", response.status_code)
        else:
            raise ApiError(f"Failed to get car: {response.text}", response.status_code) 