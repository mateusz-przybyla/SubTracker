import pytest
from datetime import date

from api.models import SubscriptionModel

def test_stats_summary_returns_correct_data(client, db_session, jwt, sample_user):
    # Arrange: subs in November
    sub1 = SubscriptionModel(
        user_id=sample_user.id,
        name="Netflix",
        price="29.99",
        billing_cycle="monthly",
        next_payment_date=date(2025, 11, 5),
        category="entertainment"
    )
    sub2 = SubscriptionModel(
        user_id=sample_user.id,
        name="Spotify",
        price="22.47",
        billing_cycle="monthly",
        next_payment_date=date(2025, 11, 10),
        category="music"
    )
    db_session.add_all([sub1, sub2])
    db_session.commit()

    # Act: check November
    response = client.get("/stats/summary?month=2025-11", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == "2025-11"
    assert data['total_spent'] == pytest.approx(52.46)
    assert data['by_category'] == {
        "entertainment": 29.99,
        "music": 22.47,
    }

def test_stats_summary_defaults_to_current_month(client, db_session, jwt, sample_user):
    # Arrange: sub in current month
    today = date.today()
    current_month = today.strftime("%Y-%m")

    sub = SubscriptionModel(
        user_id=sample_user.id,
        name="Netflix",
        price="29.99",
        billing_cycle="monthly",
        next_payment_date=today,
        category="entertainment"
    )
    db_session.add(sub)
    db_session.commit()

    # Act: request without query param
    response = client.get("/stats/summary", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == current_month
    assert data['total_spent'] == pytest.approx(29.99)
    assert data['by_category'] == {"entertainment": 29.99}

def test_stats_summary_filters_by_month(client, db_session, jwt, sample_user):
    # Arrange: sub in December
    sub = SubscriptionModel(
        user_id=sample_user.id,
        name="Disney+",
        price="10.00",
        billing_cycle="monthly",
        next_payment_date=date(2025, 12, 1),
        category="entertainment"
    )
    db_session.add(sub)
    db_session.commit()

    # Act: check November
    response = client.get("/stats/summary?month=2025-11", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == "2025-11"
    assert data['total_spent'] == 0.0
    assert data['by_category'] == {}

def test_stats_summary_requires_auth(client):
    # Act: request without jwt
    response = client.get("/stats/summary?month=2025-11")

    # Assert
    assert response.status_code == 401

def test_stats_summary_validates_month_format(client, jwt):
    # Act: fake month
    response = client.get("/stats/summary?month=2025-13", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 422
    data = response.get_json()
    assert "month" in data['errors']['query']
    assert data['errors']['query']['month'] == ["Month must be between 01 and 12."]