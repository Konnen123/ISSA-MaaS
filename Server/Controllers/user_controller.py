from flask import Blueprint, jsonify
from flask_apispec import doc, marshal_with

from Schemas.user_schemas import UserSchema

user_bp = Blueprint('user', __name__)

@user_bp.route('/pet/<int:pet_id>', methods=['GET'])
@doc(description='Get a pet by its ID', tags=['User'])
@marshal_with(UserSchema)
def get_pet(pet_id):
    pet = {'id': pet_id, 'name': 'Fluffy'}
    return jsonify(pet)