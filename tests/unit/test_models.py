import datetime
from decimal import Decimal

from api.models import UserModel, SubscriptionModel, ReminderLogModel
from api.models.enums import BillingCycleEnum

# ---------------------------
# USER MODEL
# ---------------------------

def test_user_model_fiels():
    user = UserModel(username="test", email="a@b.com", password="secret")
    assert user.username == "test"
    assert user.email == "a@b.com"
    assert user.password == "secret"

# ---------------------------
# SUBSCRIPTION MODEL
# ---------------------------

def test_subscription_model_fields():
    subscription = SubscriptionModel(
        name="Netflix",
        price=Decimal("29.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=datetime.date(2024, 7, 15),
        user_id=1
    )
    assert subscription.name == "Netflix"
    assert subscription.price == Decimal("29.99")
    assert subscription.billing_cycle == BillingCycleEnum.monthly
    assert subscription.next_payment_date == datetime.date(2024, 7, 15)
    assert subscription.user_id == 1

# ---------------------------
# REMINDER LOG MODEL
# ---------------------------

def test_reminder_log_model_fields():
    reminder_log = ReminderLogModel(
        subscription_id=1,
        success=True
    )
    assert reminder_log.subscription_id == 1
    assert reminder_log.success is True