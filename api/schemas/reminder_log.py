from marshmallow import Schema, fields

class ReminderLogSchema(Schema):
    id = fields.Int(dump_only=True)
    subscription_id = fields.Int(required=True)
    message = fields.Str()
    success = fields.Bool()
    sent_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", dump_only=True)