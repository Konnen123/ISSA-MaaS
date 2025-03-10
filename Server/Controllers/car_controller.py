import random
import socket

from flask import Blueprint, request
from flask_apispec import use_kwargs

from Schemas.register_car_schema import RegisterCarSchema
from Services.session_service import SessionService
from Utils import database_connection

car_bp = Blueprint("car", __name__, url_prefix="/api/v1")

connection = database_connection.get_connection()
cursor = connection.cursor()

@car_bp.route('/cars/available', methods=['GET'])
def get_cars_available():
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars WHERE available = 1')
    cars = cursor.fetchall()

    return {'cars': cars}, 200

@car_bp.route('/cars', methods=['POST'])
@use_kwargs(RegisterCarSchema, location='json')
def add_car(**kwargs):
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    car = request.json
    car_port = random.randint(10000, 65535)

    cursor.execute('''
        INSERT INTO cars (car_plate, doors, fuel, registration_number, available, lights, locked, car_port)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
    car['car_plate'], car['doors'], car['fuel'], car['registration_number'], car['available'], car['lights'], 1, car_port))
    connection.commit()

    return {'car_id': f'{cursor.lastrowid}', 'car_port': f'{car_port}'}, 201

@car_bp.route('/cars/<int:id>', methods=['PATCH'])
def select_car(id):
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars WHERE id = ?', (id,))
    car = cursor.fetchone()

    if car is None:
        return {'message': 'Car not found'}, 404

    if car[5] == 0:
        return {'message': 'Car is not available'}, 400

    cursor.execute('UPDATE cars SET available = 0 WHERE id = ?', (id,))
    connection.commit()

    return {}, 202

@car_bp.route('/cars/rental/<int:id>', methods=['POST'])
def start_rent_car(id):
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars WHERE id = ?', (id,))
    car = cursor.fetchone()

    if car is None:
        return {'message': 'Car not found'}, 404

    if car[5] == 1:
        return {'message': 'Car must be selected first'}, 400

    if car[7] == 0:
        return {'message': 'Car is already unlocked'}, 400

    cursor.execute('UPDATE cars SET locked = 0 WHERE id = ?', (id,))
    connection.commit()

    notify_car(id, car[8], 'rented')

    return {}, 202

@car_bp.route('/cars/rental/<int:id>', methods=['DELETE'])
def finish_rent_car(id):
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars WHERE id = ?', (id,))
    car = cursor.fetchone()

    if car is None:
        return {'message': 'Car not found'}, 404

    if car[7] == 1:
        return {'message': 'Car is already locked'}, 400

    if car[6] == 0:
        return {'message': 'Turn off the lights first!'}, 400

    cursor.execute('UPDATE cars SET locked = 1 AND available = 1 WHERE id = ?', (id,))
    connection.commit()

    notify_car(id, car[8], 'finished renting')

    return {}, 202

@car_bp.route('/cars/all', methods=['GET'])
def get_all_cars():
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars')
    cars = cursor.fetchall()

    return {'cars': cars}, 200

@car_bp.route('/cars/<int:id>', methods=['GET'])
def get_car_by_id(id):
    session_token = request.cookies.get('session_token')

    if not SessionService().is_session_active(session_token):
        return {'message': 'Unauthorized'}, 401

    cursor.execute('SELECT * FROM cars WHERE id = ?', (id,))
    car = cursor.fetchone()

    if car is None:
        return {'message': 'Car not found'}, 404

    return {'car': car}, 200

def notify_car(car_id, car_port, status):
    cli_app_host = 'localhost'
    cli_app_port = car_port
    message = f'Car {car_id} is {status}'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((cli_app_host, cli_app_port))
        s.sendall(message.encode())