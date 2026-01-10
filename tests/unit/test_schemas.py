import pytest
from marshmallow import ValidationError
from decimal import Decimal
from datetime import date

from api.schemas import (
    UserRegisterSchema, 
    UserLoginSchema, 
    UserResponseSchema, 
    SubscriptionSchema, 
    SubscriptionUpdateSchema
)
from api.models import UserModel
from api.models.enums import BillingCycleEnum

# Fixtures

@pytest.fixture
def register_schema():
    return UserRegisterSchema()

@pytest.fixture
def login_schema():
    return UserLoginSchema()

@pytest.fixture
def user_response_schema():
    return UserResponseSchema()

@pytest.fixture
def subscription_schema():
    return SubscriptionSchema()

@pytest.fixture
def subscription_update_schema():
    return SubscriptionUpdateSchema()

# Tests for RegisterSchema, ResponseSchema

def test_register_schema_valid_data(register_schema, user_response_schema):
    user_dict = {
        "username": "test_user", 
        "email": "test@example.com", 
        "password": "abc123"
    }

    loaded = register_schema.load(user_dict)
    assert loaded['username'] == "test_user"
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

    user_obj = UserModel(username="test_user", email="test@example.com", password="abc123")
    dumped = user_response_schema.dump(user_obj)
    assert dumped['username'] == "test_user"
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped
    assert "created_at" in dumped

def test_register_schema_missing_fields(register_schema):
    user_dict = {"email": "test@example.com"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors
    assert "username" in errors

def test_register_schema_password_too_short(register_schema):
    user_dict = {
        "username": "test_user", 
        "email": "test@example.com", 
        "password": "abc"
    }

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_register_schema_invalid_email(register_schema):
    user_dict = {
        "username": "test_user", 
        "email": "not-an-email", 
        "password": "abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors

def test_register_schema_username_too_short(register_schema):
    user_dict = {"username": "ab", "email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors

# Tests for LoginSchema

def test_login_schema_valid_data(login_schema):
    user_dict = {
        "email": "test@example.com", 
        "password": "abc123"
    }

    loaded = login_schema.load(user_dict)
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

def test_login_schema_missing_fields(login_schema):
    user_dict = {"email": "test@example.com"}

    with pytest.raises(ValidationError) as exc_info:
        login_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_login_schema_invalid_email(login_schema):
    user_dict = {
        "email": "not-an-email", 
        "password": "abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        login_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors

# Tests for SubscriptionSchema

def test_subscription_schema_valid(subscription_schema):
    data = {
        "name": "Netflix",
        "price": "29.99",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-11-01",
        "category": "entertainment"
    }

    loaded = subscription_schema.load(data)

    assert loaded['name'] == "Netflix"
    assert Decimal(loaded['price']) == Decimal("29.99")
    assert loaded['billing_cycle'] == BillingCycleEnum.monthly
    assert isinstance(loaded['next_payment_date'], date)
    assert loaded['category'] == "entertainment"

def test_subscription_schema_invalid_price(subscription_schema):
    data = {
        "name": "Spotify",
        "price": "invalid-price",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-12-01",
        "category": "music"
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "price" in errors

def test_subscription_schema_negative_price(subscription_schema):
    data = {
        "name": "Amazon Prime",
        "price": "-9.99",
        "billing_cycle": "yearly",
        "next_payment_date": "2026-01-01",
        "category": "entertainment"
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "price" in errors

def test_subscription_schema_invalid_date(subscription_schema):
    data = {
        "name": "Hulu",
        "price": "19.99",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-13-01",  # Invalid month
        "category": "entertainment"
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "next_payment_date" in errors


def test_subscription_schema_missing_required_fields(subscription_schema):
    data = {
        "price": "19.99",
        "billing_cycle": "monthly"
    }
    
    with pytest.raises(Exception) as exc_info:
        subscription_schema.load(data) 
    
    errors = exc_info.value.messages
    assert "name" in errors
    assert "next_payment_date" in errors

def test_subscription_schema_invalid_billing_cycle(subscription_schema):
    data = {
        "name": "Disney+",
        "price": "15.99",
        "billing_cycle": "invalid_cycle",  # Invalid billing cycle
        "next_payment_date": "2025-10-01",
        "category": "entertainment"
    }

    with pytest.raises(ValidationError) as exc_info:
        subscription_schema.load(data)

    errors = exc_info.value.messages
    assert "billing_cycle" in errors

# Tests for SubscriptionUpdateSchema

def test_subscription_update_schema_partial_update(subscription_update_schema):
    data = {"price": "15.00"}

    loaded = subscription_update_schema.load(data)

    assert loaded['price'] == Decimal("15.00")
    assert "name" not in loaded
    assert "billing_cycle" not in loaded
    assert "next_payment_date" not in loaded

def test_subscription_update_schema_invalid_enum(subscription_update_schema):
    data = {"billing_cycle": "monthly1"}

    with pytest.raises(ValidationError) as exc_info:
        subscription_update_schema.load(data)

    errors = exc_info.value.messages
    assert "billing_cycle" in errors

def test_subscription_update_schema_no_fields(subscription_update_schema):
    data = {}

    loaded = subscription_update_schema.load(data)

    assert loaded == {}