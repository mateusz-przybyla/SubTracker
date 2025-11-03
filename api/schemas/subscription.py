from marshmallow import Schema, fields, validate

class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=120))
    price = fields.Decimal(as_string=True, required=True)
    billing_cycle = fields.Str(required=True, validate=validate.Length(max=20))
    next_payment_date = fields.Date(required=True)
    category = fields.Str(validate=validate.Length(max=80))
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", dump_only=True)
