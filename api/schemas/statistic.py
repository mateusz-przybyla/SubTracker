from marshmallow import Schema, fields, validate, ValidationError

def validate_month(value: str) -> None:
    # Check format YYYY-MM
    if not validate.Regexp(r"^\d{4}-\d{2}$")(value):
        raise ValidationError("Month must be in YYYY-MM format.")
    # Check the scope of the month
    year, month = value.split("-")
    month_int = int(month)
    if month_int < 1 or month_int > 12:
        raise ValidationError("Month must be between 01 and 12.")

class StatsSummaryQueryArgsSchema(Schema):
    month = fields.String(
        required=False,
        validate=validate_month,
        metadata={"description": "Month in YYYY-MM format (e.g. 2025-10)"}
    )

class StatsSummarySchema(Schema):
    month = fields.String(required=True, metadata={"description": "Month in YYYY-MM format"})
    total_spent = fields.Float(required=True, metadata={"description": "Total amount spent in the month"})
    by_category = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        metadata={"description": "Breakdown of spending by category"}
    )