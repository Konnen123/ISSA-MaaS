import socket
import threading
from typing import Dict, Any, List, Optional, Callable

import typer
from rich.console import Console
from rich.table import Table

from ..utils.error_handler import handle_error, exit_with_error
from ..utils.logger import get_logger
from .api_client import ApiClient
from .auth_handler import AuthHandler

logger = get_logger()
console = Console()

# Global state for selected car
selected_car_id = None
car_socket_server = None


class CliManager:
    """Manages the CLI interface and commands."""
    _instance = None
    _app: typer.Typer = None
    _api_client: ApiClient = None
    _auth_handler: AuthHandler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CliManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the CLI manager."""
        self._app = typer.Typer(help="MaaS Client - Mobility as a Service")
        self._api_client = ApiClient()
        self._auth_handler = AuthHandler()
        self._register_commands()
        logger.debug("CLI manager initialized")

    def _register_commands(self):
        """Register all available commands."""
        # Authentication commands
        self._app.command(name="register")(self.register)
        self._app.command(name="login")(self.login)
        self._app.command(name="logout")(self.logout)
        
        # Car commands
        self._app.command(name="cars")(self.list_cars)
        self._app.command(name="select-car")(self.select_car)
        self._app.command(name="start-rent")(self.start_rent)
        self._app.command(name="finish-rent")(self.finish_rent)

    @handle_error
    def register(
        self,
        email: str = typer.Option(..., "--email", help="User email"),
        password: str = typer.Option(..., "--password", help="User password"),
        first_name: str = typer.Option(..., "--first-name", help="User first name"),
        last_name: str = typer.Option(..., "--last-name", help="User last name"),
        address: str = typer.Option(..., "--address", help="User address"),
        card_number: str = typer.Option(..., "--card-number", help="User card number")
    ):
        """Register a new user."""
        console.print("[bold]Register a new user[/bold]")
        
        user_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "card_number": card_number
        }
        
        self._auth_handler.register(user_data)

    @handle_error
    def login(
        self,
        email: str = typer.Option(..., "--email", help="User email"),
        password: str = typer.Option(..., "--password", help="User password")
    ):
        """Login with credentials."""
        console.print("[bold]Login[/bold]")
        self._auth_handler.login(email, password)

    @handle_error
    def logout(self):
        """Logout current user."""
        self._auth_handler.logout()
        global selected_car_id
        selected_car_id = None
        
        # Stop socket server if running
        global car_socket_server
        if car_socket_server:
            car_socket_server.shutdown()
            car_socket_server = None

    @handle_error
    def list_cars(self):
        """List all available cars."""
        self._auth_handler.require_auth()
        
        cars = self._api_client.get_available_cars()
        if not cars:
            console.print("[yellow]No cars available at the moment.[/yellow]")
            return
        
        table = Table(title="Available Cars")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Plate", style="green")
        table.add_column("Doors", justify="right")
        table.add_column("Fuel", justify="right")
        table.add_column("Registration Number")
        table.add_column("Port", justify="right")
        
        for car in cars:
            table.add_row(
                str(car[0]),  # ID
                car[1],       # Plate
                str(car[2]),  # Doors
                str(car[3]),  # Fuel
                car[4],       # Registration Number
                str(car[8])   # Port
            )
        
        console.print(table)

    @handle_error
    def select_car(self, car_id: int):
        """Select a car by ID."""
        self._auth_handler.require_auth()
        
        # First, check if the car exists and get its details
        car = self._api_client.get_car_by_id(car_id)
        if not car:
            console.print(f"[red]Error:[/red] Car {car_id} not found")
            return False
        
        # Try to select the car
        if self._api_client.select_car(car_id):
            global selected_car_id
            selected_car_id = car_id
            console.print(f"[green]Success:[/green] Car {car_id} selected")
            
            # Start socket server to listen for car notifications
            return self._start_socket_server(car_id)
        return False

    @handle_error
    def start_rent(self, car_id: Optional[int] = None):
        """Start renting a car."""
        self._auth_handler.require_auth()
        
        global selected_car_id
        car_id_to_use = car_id or selected_car_id
        
        if not car_id_to_use:
            console.print("[yellow]Warning:[/yellow] No car selected. Please select a car first.")
            return False
        
        # Verify that we have a valid socket server running
        global car_socket_server
        if not car_socket_server or not car_socket_server.running:
            console.print("[yellow]Warning:[/yellow] Socket server not running. Attempting to restart...")
            if not self._start_socket_server(car_id_to_use):
                console.print("[red]Error:[/red] Could not start socket server. Car notifications will not work.")
                return False
        
        if self._api_client.start_rent(car_id_to_use):
            console.print(f"[green]Success:[/green] Started renting car {car_id_to_use}")
            return True
        return False

    @handle_error
    def finish_rent(self, car_id: Optional[int] = None):
        """Finish renting a car."""
        self._auth_handler.require_auth()
        
        global selected_car_id
        car_id_to_use = car_id or selected_car_id
        
        if not car_id_to_use:
            console.print("[yellow]Warning:[/yellow] No car selected. Please select a car first.")
            return False
        
        if self._api_client.finish_rent(car_id_to_use):
            console.print(f"[green]Success:[/green] Finished renting car {car_id_to_use}")
            selected_car_id = None
            
            # Stop socket server
            global car_socket_server
            if car_socket_server:
                car_socket_server.shutdown()
                car_socket_server = None
            return True
        return False

    def _get_car_port(self, car_id: int) -> Optional[int]:
        """Get the port for the specified car from the server."""
        car = self._api_client.get_car_by_id(car_id)
        if car and len(car) > 8:
            return car[8]  # Port is at index 8
        logger.error(f"Could not get port for car {car_id}")
        return None

    def _start_socket_server(self, car_id: int):
        """Start a socket server to listen for car notifications."""
        global car_socket_server
        if car_socket_server:
            car_socket_server.shutdown()
        
        # Get the port for the selected car
        car_port = self._get_car_port(car_id)
        if not car_port:
            console.print("[red]Error:[/red] Could not determine the port for the selected car")
            return False
        
        try:
            # Create a socket server on the specific port
            car_socket_server = CarSocketServer(port=car_port)
            car_socket_server.start()
            logger.info(f"Socket server started on port {car_port}")
            console.print(f"[blue]Info:[/blue] Listening for car notifications on port {car_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start socket server: {str(e)}")
            console.print(f"[red]Error:[/red] Failed to start socket server: {str(e)}")
            return False

    def run(self):
        """Run the CLI application."""
        self._app()


class CarSocketServer(threading.Thread):
    """Socket server to listen for car notifications."""
    def __init__(self, host='localhost', port=0):
        super().__init__()
        self.daemon = True
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.running = True
            logger.info(f"Socket server started on port {self.port}")
        except OSError as e:
            logger.error(f"Failed to bind to port {self.port}: {str(e)}")
            raise

    def run(self):
        """Run the socket server."""
        logger.debug(f"Socket server listening on {self.host}:{self.port}")
        console.print(f"[blue]Info:[/blue] Listening for car notifications on port {self.port}")
        
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                data = client_socket.recv(1024).decode()
                logger.info(f"Received notification: {data}")
                console.print(f"[blue]Car Notification:[/blue] {data}")
                client_socket.close()
            except Exception as e:
                if self.running:
                    logger.error(f"Socket error: {str(e)}")
                break

    def shutdown(self):
        """Shutdown the socket server."""
        self.running = False
        try:
            # Connect to the socket to break the accept() call
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            self.server_socket.close()
            logger.info("Socket server shutdown")
        except Exception as e:
            logger.error(f"Error shutting down socket server: {str(e)}") 