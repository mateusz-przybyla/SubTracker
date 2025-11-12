from marshmallow import Schema, fields

class ReminderLogSchema(Schema):
    id = fields.Int(dump_only=True)
    subscription_id = fields.Int(required=True, dump_only=True)
    message = fields.Str()
    success = fields.Bool(required=True)
    sent_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", dump_only=True)