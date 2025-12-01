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

class StatsSendTestSchema(Schema):
    email = fields.Email(required=True, metadata={"description": "Target email address"})
    month = fields.String(required=True, metadata={"description": "Month in YYYY-MM format"})
    total_spent = fields.Float(required=True, metadata={"description": "Total amount spent"})
    by_category = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        required=True,
        metadata={"description": "Breakdown of spending by category"}
    )