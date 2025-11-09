import pytest
import datetime
from decimal import Decimal

from api.models import SubscriptionModel
from api.models.enums import BillingCycleEnum

@pytest.fixture
def sample_subscription(db_session, sample_user):
    subscription = SubscriptionModel(
        name="Netflix",
        price=Decimal("29.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=datetime.date(2025, 1, 15),
        user_id=sample_user.id,
    )
    db_session.add(subscription)
    db_session.commit()
    return subscription

def test_create_subscription_success(client, db_session, jwt):
    data = {
        "name": "Netflix",
        "price": "29.99",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-07-15"
    }

    response = client.post("/subscription", json=data, headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 201
    assert response.json['name'] == "Netflix"

    created_sub = db_session.query(SubscriptionModel).filter_by(name="Netflix").first()
    assert created_sub.price == Decimal("29.99")
    assert created_sub is not None

def test_create_subscription_duplicate_name(client, jwt, sample_subscription):
    data = {
        "name": "Netflix",
        "price": "25.00",
        "billing_cycle": "monthly",
        "next_payment_date": "2025-03-01"
    }

    response = client.post("/subscription", json=data, headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 409
    assert response.json['message'] == "You already have a subscription with this name."
    assert SubscriptionModel.query.count() == 1

def test_create_subscription_missing_field(client, jwt):
    data = {
        "price": "12.99",
        "billing_cycle": "monthly",
    }

    response = client.post("/subscription", json=data, headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 422
    assert "name" in response.json['errors']['json']

def test_get_user_subscriptions(client, db_session, jwt, sample_subscription):
    another_subscription = SubscriptionModel(
        name="Spotify",
        price=Decimal("19.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=datetime.date(2025, 7, 10),
        user_id=sample_subscription.id
    )
    db_session.add(another_subscription)
    db_session.commit()
     
    response = client.get("/subscription", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert len(response.json) == 2

    names = [sub['name'] for sub in response.json]
    assert "Netflix" in names
    assert "Spotify" in names

def test_get_user_subscriptions_empty(client, jwt):
    response = client.get("/subscription", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json == []

def test_get_subscription_by_id_success(client, jwt, sample_subscription):
    response = client.get(f"/subscription/{sample_subscription.id}", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json['name'] == "Netflix"

def test_get_subscription_by_id_not_found(client, jwt):
    response = client.get("/subscription/999", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Subscription not found."

def test_get_subscription_by_id_unauthorized(client, sample_subscription):
    response = client.get(f"/subscription/{sample_subscription.id}")

    assert response.status_code == 401

def test_update_subscription_success(client, db_session, jwt, sample_subscription):
    update_data = {"price": "35.50", "billing_cycle": "yearly"}

    response = client.put(f"/subscription/{sample_subscription.id}", json=update_data, headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json['price'] == "35.50"
    assert response.json['billing_cycle'] == "yearly"

    updated_sub = db_session.query(SubscriptionModel).get(sample_subscription.id)
    assert updated_sub.price == Decimal("35.50")

def test_update_subscription_not_found(client, jwt):
    update_data = {"price": "35.50"}

    response = client.put("/subscription/999", json=update_data, headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Subscription not found."

def test_delete_subscription_success(client, db_session, jwt, sample_subscription):
    response = client.delete(f"/subscription/{sample_subscription.id}", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json['message'] == "Subscription deleted."

    deleted_sub = db_session.query(SubscriptionModel).filter_by(id=sample_subscription.id).first()
    assert deleted_sub is None

def test_delete_subscription_not_found(client, jwt):
    response = client.delete("/subscription/999", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Subscription not found."