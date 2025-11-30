from marshmallow import Schema, fields

class ReminderSendTestSchema(Schema):
    email = fields.Email(
        required=True,
        metadata={"description": "Target email address"}
    )
    subscription_name = fields.Str(
        required=False,
        metadata={"description": "Name of subscription"}
    )
    next_payment_date = fields.Date(
        required=False,
        metadata={"description": "Date in YYYY-MM-DD format"}
    )