from marshmallow import Schema, fields

class RegisterCarSchema(Schema):
    model = fields.Str(required=True)
    car_plate = fields.Str(required=True)
    doors = fields.Int(required=True)
    fuel = fields.Int(required=True)
    registration_number = fields.Str(required=True)
    available = fields.Bool(required=True)
    lights = fields.Bool(required=True)