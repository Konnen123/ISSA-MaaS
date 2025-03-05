import random

from flask import Blueprint
from flask_apispec import use_kwargs
from werkzeug.security import generate_password_hash, check_password_hash

from Schemas.login_schema import LoginSchema
from Schemas.register_schema import RegisterSchema
from Schemas.user_schemas import UserSchema
from Services.session_service import SessionService
from Utils import database_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1")

connection = database_connection.get_connection()
cursor = connection.cursor()

@auth_bp.route('/login', methods=['POST'])
@use_kwargs(LoginSchema, location='json')
def login_user(**kwargs):
    email = kwargs.get('email')
    password = kwargs.get('password')

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user is not None and email == user[1] and check_password_hash(user[2], password):
        session_token = SessionService().create_session(user)
        return {'session_token': f'{session_token}'}, 200

    return {'message': 'Invalid credentials'}, 401

@auth_bp.route('/register', methods=['POST'])
@use_kwargs(RegisterSchema, location='json')
def register_user(**kwargs):
    user = UserSchema().load(kwargs)

    cursor.execute('''
        INSERT INTO users (email, password, first_name, last_name, address, card_number)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
    user['email'], generate_password_hash(user['password']), user['first_name'], user['last_name'], user['address'], user['card_number']))
    connection.commit()

    return {'message': 'User registered successfully'}, 201