import sys
from typing import Callable, Any, Optional

import requests
from rich.console import Console

from .logger import get_logger

logger = get_logger()
console = Console()


class ClientError(Exception):
    """Base exception for client errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(ClientError):
    """Exception raised for authentication errors."""
    pass


class ApiError(ClientError):
    """Exception raised for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class ConnectionError(ClientError):
    """Exception raised for connection errors."""
    pass


def handle_error(func: Callable) -> Callable:
    """Decorator to handle errors in functions."""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            console.print("[bold red]Error:[/bold red] Failed to connect to the server. Please check your internet connection.")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {str(e)}")
            console.print("[bold red]Error:[/bold red] Request timed out. Please try again later.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return None
        except AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            console.print(f"[bold red]Authentication Error:[/bold red] {e.message}")
            return None
        except ApiError as e:
            logger.error(f"API error: {str(e)}")
            status_msg = f" (Status code: {e.status_code})" if e.status_code else ""
            console.print(f"[bold red]API Error:[/bold red] {e.message}{status_msg}")
            return None
        except ClientError as e:
            logger.error(f"Client error: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
            return None
    return wrapper


def exit_with_error(message: str, exit_code: int = 1) -> None:
    """Exit the application with an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    logger.error(message)
    sys.exit(exit_code) 