from marshmallow import Schema, fields

class RegisterSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    address = fields.Str(required=True)
    card_number = fields.Str(required=True)