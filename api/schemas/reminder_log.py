from marshmallow import Schema, fields

class ReminderLogResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    subscription_id = fields.Int(dump_only=True)
    message = fields.Str(dump_only=True)
    success = fields.Bool(dump_only=True)
    sent_at = fields.DateTime(dump_only=True)