# MaaS Client

A command-line interface client for the Mobility as a Service (MaaS) system.

## Features

- User Registration
- User Login/Logout
- View Available Cars
- Select Car
- Start Rent
- Finish Rent

## Installation

1. Clone the repository
2. Navigate to the Client directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the Client directory with the following content:

```
API_BASE_URL=http://localhost:5000/api/v1
```

## Usage

Run the client:

```bash
python src/main.py
```

Available commands:

- `register` - Register a new user
- `login` - Login with existing credentials
- `logout` - Logout current user
- `cars` - View available cars
- `select-car` - Select a car by ID
- `start-rent` - Start renting the selected car
- `finish-rent` - Finish renting the car

## Example

```bash
# Register a new user
python src/main.py register

# Login
python src/main.py login

# View available cars
python src/main.py cars

# Select a car
python src/main.py select-car 1

# Start renting
python src/main.py start-rent 1

# Finish renting
python src/main.py finish-rent 1
``` 