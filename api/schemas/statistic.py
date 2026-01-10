import re
from marshmallow import Schema, fields, ValidationError

def validate_month(value: str) -> None:
    if not re.match(r"^\d{4}-\d{2}$", value):
        raise ValidationError("Month must be in YYYY-MM format.")

    year, month = value.split("-")
    month_int = int(month)

    if not 1 <= month_int <= 12:
        raise ValidationError("Month must be between 01 and 12.")

class StatsSummaryQueryArgsSchema(Schema):
    month = fields.String(
        required=False,
        validate=validate_month,
        metadata={"description": "Month in YYYY-MM format (e.g. 2025-10)"}
    )

class StatsSummaryResponseSchema(Schema):
    month = fields.String(dump_only=True)
    total_spent = fields.Decimal(as_string=True, dump_only=True)
    by_category = fields.Dict(
        keys=fields.String(),
        values=fields.Decimal(as_string=True),
        dump_only=True
    )