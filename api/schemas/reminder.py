from marshmallow import Schema, fields

class UpcomingQueryArgsSchema(Schema):
    days = fields.Int(
        required=False,
        load_default=7,
        metadata={"description": "Number of days ahead to include in upcoming payments."}
    )