from datetime import date
from decimal import Decimal

def test_stats_summary_returns_correct_data(client, jwt, sample_user, subscription_factory):
    # Arrange: subs in November
    subscription_factory(
        user_id=sample_user.id,
        name="Netflix",
        price=Decimal("29.99"),
        category="entertainment",
        next_payment_date=date(2025, 11, 5)
    )
    subscription_factory(
        user_id=sample_user.id,
        name="Spotify",
        price=Decimal("22.47"),
        category="music",
        next_payment_date=date(2025, 11, 10)
    )

    # Act: check November
    response = client.get("/stats/summary?month=2025-11", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == "2025-11"
    assert data['total_spent'] == "52.46"
    assert data['by_category'] == {
        "entertainment": "29.99",
        "music": "22.47"
    }

def test_stats_summary_defaults_to_current_month(client, jwt, sample_user, subscription_factory):
    # Arrange: sub in current month
    today = date.today()
    current_month = today.strftime("%Y-%m")

    subscription_factory(
        user_id=sample_user.id,
        next_payment_date=today,
    )

    # Act: request without query param
    response = client.get("/stats/summary", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == current_month
    assert data['total_spent'] == "29.99"
    assert data['by_category'] == {"entertainment": "29.99"}

def test_stats_summary_filters_by_month(client, jwt, sample_user, subscription_factory):
    # Arrange: sub in December
    subscription_factory(
        user_id=sample_user.id,
        name="Disney+",
        price=Decimal("10.00"),
        category="entertainment",
        next_payment_date=date(2025, 12, 1),
    )

    # Act: check November
    response = client.get("/stats/summary?month=2025-11", headers={"Authorization": f"Bearer {jwt}"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['month'] == "2025-11"
    assert data['total_spent'] == "0.00"
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