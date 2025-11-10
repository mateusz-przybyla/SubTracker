from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal

from api.models.enums import BillingCycleEnum
from api.utils.validators import validate_future_date

class SubscriptionBaseSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    category = fields.Str(validate=validate.Length(max=80))
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", dump_only=True)
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S", dump_only=True)

    def get_billing_cycle(self, obj):
        return obj.billing_cycle.value if obj.billing_cycle else None

    def load_billing_cycle(self, value):
        try:
            return BillingCycleEnum(value)
        except ValueError:
            raise ValidationError(
                f"Invalid billing cycle '{value}'. Must be one of: "
                f"{', '.join([e.value for e in BillingCycleEnum])}"
            )
        
class SubscriptionSchema(SubscriptionBaseSchema):
    name = fields.Str(validate=validate.Length(max=120), required=True)
    price = fields.Decimal(as_string=True, required=True, validate=validate.Range(min=Decimal("0.01")))
    billing_cycle = fields.Method(
        serialize="get_billing_cycle", 
        deserialize="load_billing_cycle", 
        required=True,
        metadata={
            "type": "string",
            "enum": [e.value for e in BillingCycleEnum],
            "description": "Billing cycle type."
        }
    )
    next_payment_date = fields.Date(required=True, validate=validate_future_date)

class SubscriptionUpdateSchema(SubscriptionBaseSchema):
    name = fields.Str(validate=validate.Length(max=120))
    price = fields.Decimal(as_string=True, validate=validate.Range(min=Decimal("0.01")))
    billing_cycle = fields.Method(
        serialize="get_billing_cycle", 
        deserialize="load_billing_cycle",
        metadata={
            "type": "string",
            "enum": [e.value for e in BillingCycleEnum],
            "description": "Billing cycle type."
        }
    )
    next_payment_date = fields.Date(validate=validate_future_date)