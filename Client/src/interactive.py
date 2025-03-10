#!/usr/bin/env python3
"""
Interactive MaaS Client - Mobility as a Service Client Application

This script provides an interactive loop for the MaaS client application.
"""
import os
import sys
import socket
import threading
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

# Add the parent directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.core.auth_handler import AuthHandler
from src.core.api_client import ApiClient
from src.core.cli_manager import CliManager
from src.core.cli_manager import CarSocketServer
import src.core.cli_manager as cli_manager_module

logger = get_logger()
console = Console()

# Add at the top with other global variables
is_renting = False

# Update the COMMANDS list to separate available commands during rental
NORMAL_COMMANDS = [
    "register",
    "login",
    "logout",
    "cars",
    "select-car",
    "start-rent",
    "finish-rent",
    "help",
    "exit"
]

RENTAL_COMMANDS = [
    "finish-rent",
    "help",
    "exit"
]

def print_welcome():
    """Print welcome message."""
    console.print(Panel.fit(
        "[bold blue]MaaS Interactive Client[/bold blue]\n"
        "Type [bold green]help[/bold green] to see available commands or [bold red]exit[/bold red] to quit.",
        title="Welcome",
        border_style="blue"
    ))

def print_help():
    """Print help message with available commands."""
    global is_renting
    
    if is_renting:
        help_text = "\n".join([
            "[bold red]Currently renting a car. Only the following commands are available:[/bold red]",
            "  [green]finish-rent[/green] - Finish renting the current car",
            "  [green]help[/green] - Show this help message",
            "  [green]exit[/green] - Exit the application"
        ])
    else:
        help_text = "\n".join([
            "[bold]Available commands:[/bold]",
            "  [green]register[/green] - Register a new user",
            "  [green]login[/green] - Login with existing credentials",
            "  [green]logout[/green] - Logout current user",
            "  [green]cars[/green] - View available cars",
            "  [green]select-car[/green] - Select a car by ID",
            "  [green]start-rent[/green] - Start renting the selected car",
            "  [green]finish-rent[/green] - Finish renting the car",
            "  [green]help[/green] - Show this help message",
            "  [green]exit[/green] - Exit the application"
        ])
    console.print(Panel(help_text, title="Help", border_style="green"))

def parse_command(input_str: str) -> str:
    """Parse the input string to get the command."""
    return input_str.strip().lower()

def get_car_port(car_id: int) -> Optional[int]:
    """Get the port for the specified car from the server."""
    api_client = ApiClient()
    car = api_client.get_car_by_id(car_id)
    if car and len(car) > 8:
        return car[8]  # Port is at index 8
    logger.error(f"Could not get port for car {car_id}")
    return None

def start_socket_server(car_id: int):
    """Start a socket server to listen for car notifications."""
    if hasattr(cli_manager_module, 'car_socket_server') and cli_manager_module.car_socket_server:
        cli_manager_module.car_socket_server.shutdown()
    
    # Get the port for the selected car
    car_port = get_car_port(car_id)
    if not car_port:
        console.print("[red]Error:[/red] Could not determine the port for the selected car.")
        return False
        
    try:
        # Create a socket server on the specific port
        cli_manager_module.car_socket_server = CarSocketServer(port=car_port)
        cli_manager_module.car_socket_server.start()
        logger.info(f"Socket server started on port {car_port}")
        console.print(f"[blue]Info:[/blue] Listening for car notifications on port {car_port}")
        return True
    except Exception as e:
        logger.error(f"Failed to start socket server: {str(e)}")
        console.print(f"[red]Error:[/red] Failed to start socket server: {str(e)}")
        return False

def stop_socket_server():
    """Stop the socket server."""
    if hasattr(cli_manager_module, 'car_socket_server') and cli_manager_module.car_socket_server:
        cli_manager_module.car_socket_server.shutdown()
        cli_manager_module.car_socket_server = None
        logger.info("Socket server stopped")

def handle_register():
    """Handle the register command with interactive prompts."""
    console.print("[bold]Register a new user[/bold]")
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    confirm_password = Prompt.ask("Confirm Password", password=True)
    
    if password != confirm_password:
        console.print("[red]Error:[/red] Passwords do not match")
        return
    
    first_name = Prompt.ask("First Name")
    last_name = Prompt.ask("Last Name")
    address = Prompt.ask("Address")
    card_number = Prompt.ask("Card Number")
    
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    cli_manager.register(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        address=address,
        card_number=card_number
    )

def handle_login():
    """Handle the login command with interactive prompts."""
    console.print("[bold]Login[/bold]")
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    cli_manager.login(email=email, password=password)

def handle_logout():
    """Handle the logout command."""
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    cli_manager.logout()
    
    # Clear selected car and stop socket server
    cli_manager_module.selected_car_id = None
    stop_socket_server()

def handle_cars():
    """Handle the cars command."""
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    cli_manager.list_cars()

def handle_select_car():
    """Handle the select-car command with interactive prompts."""
    console.print("[bold]Select a car[/bold]")
    car_id = IntPrompt.ask("Car ID")
    
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    
    # First, check if the car exists
    car = cli_manager._api_client.get_car_by_id(car_id)
    if not car:
        console.print(f"[red]Error:[/red] Car {car_id} not found")
        return False
    
    if cli_manager.select_car(car_id=car_id):
        # Update the global selected_car_id in the cli_manager module
        cli_manager_module.selected_car_id = car_id
        console.print(f"[green]Debug:[/green] Set selected_car_id to {car_id} in cli_manager module")
        return True
    return False

def handle_start_rent():
    """Handle the start-rent command."""
    global is_renting
    
    # Get the selected car ID from the cli_manager module
    car_id = cli_manager_module.selected_car_id
    
    if not car_id:
        console.print("[yellow]Warning:[/yellow] No car selected. Please select a car first.")
        return
    
    console.print(f"[green]Debug:[/green] Using selected_car_id: {car_id}")
    
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    
    # Verify that we have a valid socket server running
    if not cli_manager_module.car_socket_server or not cli_manager_module.car_socket_server.running:
        console.print("[yellow]Warning:[/yellow] Socket server not running. Attempting to restart...")
        if not start_socket_server(car_id):
            console.print("[red]Error:[/red] Could not start socket server. Car notifications will not work.")
            return False
    
    if cli_manager.start_rent(car_id=car_id):
        is_renting = True
        console.print("[bold green]You are now renting a car. Only finish-rent, help, and exit commands are available.[/bold green]")
        return True
    return False

def handle_finish_rent():
    """Handle the finish-rent command."""
    global is_renting
    
    # Get the selected car ID from the cli_manager module
    car_id = cli_manager_module.selected_car_id
    
    if not car_id:
        console.print("[yellow]Warning:[/yellow] No car selected. Please select a car first.")
        return
    
    # Use the CLI manager directly instead of subprocess
    cli_manager = CliManager()
    if cli_manager.finish_rent(car_id=car_id):
        is_renting = False
        cli_manager_module.selected_car_id = None
        stop_socket_server()
        console.print("[bold green]Rental finished. All commands are now available.[/bold green]")

def run_command(command: str) -> None:
    """Run the specified command with interactive prompts for arguments."""
    global is_renting
    
    if command == "help":
        print_help()
        return
    
    if command == "exit":
        console.print("[yellow]Exiting...[/yellow]")
        stop_socket_server()
        sys.exit(0)
    
    # Check if command is allowed during rental
    if is_renting and command not in RENTAL_COMMANDS:
        console.print("[red]Error:[/red] This command is not available while renting a car. Use 'finish-rent' to end the rental first.")
        return
    
    if command not in NORMAL_COMMANDS:
        console.print(f"[red]Unknown command: {command}[/red]")
        print_help()
        return
    
    # Handle each command with its own function to provide interactive prompts
    if command == "register":
        handle_register()
    elif command == "login":
        handle_login()
    elif command == "logout":
        handle_logout()
    elif command == "cars":
        handle_cars()
    elif command == "select-car":
        handle_select_car()
    elif command == "start-rent":
        handle_start_rent()
    elif command == "finish-rent":
        handle_finish_rent()

def main():
    """Main entry point for the interactive client."""
    try:
        print_welcome()
        
        while True:
            # Get user input
            if is_renting:
                user_input = Prompt.ask("\n[bold red]MaaS (Renting)>[/bold red]")
            else:
                user_input = Prompt.ask("\n[bold blue]MaaS>[/bold blue]")
            
            # Parse and run the command
            command = parse_command(user_input)
            if command:
                run_command(command)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting...[/yellow]")
        stop_socket_server()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        console.print(f"\n[red]Error:[/red] {str(e)}")
    finally:
        stop_socket_server()
        sys.exit(0)

if __name__ == "__main__":
    main() 