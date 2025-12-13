from datetime import date
from marshmallow import ValidationError

def validate_future_date(value):
    if value <= date.today():
        raise ValidationError(f"Date must be after {date.today().isoformat()}.")