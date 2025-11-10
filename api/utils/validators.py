import datetime
from marshmallow import ValidationError

def validate_future_date(value):
    if value <= datetime.date.today():
        raise ValidationError(f"Date must be after {datetime.date.today().isoformat()}.")
