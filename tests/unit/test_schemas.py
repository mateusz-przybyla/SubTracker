import pytest
from marshmallow import ValidationError
from decimal import Decimal
from datetime import date

from api.schemas import UserSchema, UserRegisterSchema, SubscriptionSchema, ReminderLogSchema
from api.models import UserModel

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def base_schema():
    return UserSchema()

@pytest.fixture
def register_schema():
    return UserRegisterSchema()

@pytest.fixture
def subscription_schema():
    return SubscriptionSchema()

@pytest.fixture
def reminder_log_schema():
    return ReminderLogSchema()

# -------------------------
# Tests for UserSchema (email + password only)
# -------------------------

def test_user_schema_valid_data(base_schema):
    user_dict = {"email": "test@example.com", "password": "abc123"}

    # deserialization (load)
    loaded = base_schema.load(user_dict)
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

    # serialization (dump)
    user_obj = UserModel(username="user", email="test@example.com", password="abc123")
    dumped = base_schema.dump(user_obj)
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped

def test_user_schema_missing_fields(base_schema):
    user_dict = {"email": "test@example.com"}  # missing password

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_user_schema_password_too_short(base_schema):
    user_dict = {"email": "test@example.com", "password": "abc"}

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors
    assert "Shorter than minimum length 6." in errors["password"][0]

def test_user_schema_invalid_email(base_schema):
    user_dict = {"username": "user", "email": "not-an-email", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors

# -------------------------
# Tests for UserRegisterSchema (extends UserSchema + username)
# -------------------------

def test_register_schema_valid_data(register_schema):
    user_dict = {"username": "user", "email": "test@example.com", "password": "abc123"}

    loaded = register_schema.load(user_dict)
    assert loaded['username'] == "user"
    assert loaded['email'] == "test@example.com"

    user_obj = UserModel(username="user", email="test@example.com", password="abc123")
    dumped = register_schema.dump(user_obj)
    assert dumped['username'] == "user"
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped

def test_register_schema_missing_username(register_schema):
    user_dict = {"email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors

def test_register_schema_username_too_short(register_schema):
    user_dict = {"username": "ab", "email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors
    assert "Length must be between 3 and 80." in errors["username"][0]

# ---------------------------
# SUBSCRIPTION SCHEMA
# ---------------------------

def test_subscription_schema_valid(subscription_schema):
    data = {
        "user_id": 1,
        "name": "Netflix",
        "price": "29.99",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-11-01",
        "category": "Entertainment"
    }

    loaded = subscription_schema.load(data)

    assert loaded['name'] == "Netflix"
    assert Decimal(loaded['price']) == Decimal("29.99")
    assert loaded['billing_cycle'] == "monthly"
    assert isinstance(loaded['next_payment_date'], date)

def test_subscription_schema_invalid_price(subscription_schema):
    data = {
        "user_id": 1,
        "name": "Spotify",
        "price": "invalid-price",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-12-01"
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "price" in errors

def test_subscription_schema_invalid_date(subscription_schema):
    data = {
        "user_id": 1,
        "name": "Hulu",
        "price": "19.99",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-13-01"  # Invalid month
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "next_payment_date" in errors


def test_subscription_schema_missing_required_fields(subscription_schema):
    data = {
        "user_id": 1,
        "price": "19.99",
        "billing_cycle": "monthly"
    }
    
    with pytest.raises(Exception):
        subscription_schema.load(data) 


# ---------------------------
# REMINDER LOG SCHEMA
# ---------------------------

def test_reminder_log_schema_valid(reminder_log_schema):
    data = {
        "subscription_id": 1,
        "message": "Reminder sent",
        "success": True
    }

    loaded = reminder_log_schema.load(data)

    assert loaded['subscription_id'] == 1
    assert loaded['success'] is True


def test_reminder_log_schema_missing_subscription_id(reminder_log_schema):
    data = {
        "message": "Missing sub id",
        "success": False
    }

    with pytest.raises(Exception):
        reminder_log_schema.load(data)