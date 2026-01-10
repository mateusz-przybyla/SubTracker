from datetime import date, timedelta
from decimal import Decimal

def test_reminders_upcoming_endpoint_returns_subs(client, jwt, sample_user, subscription_factory):
    today = date.today()

    subscription_factory(
        user_id=sample_user.id,
        name="Due in 3 Days",
        price=Decimal("9.99"),
        category="video",
        next_payment_date=today + timedelta(days=3),
    )

    subscription_factory(
        user_id=sample_user.id,
        name="Due in 10 Days (outside window)",
        price=Decimal("12.00"),
        category="books",
        next_payment_date=today + timedelta(days=10),
    )

    response = client.get("/reminders/upcoming?days=7", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    data = response.get_json()
    names = {sub['name'] for sub in data}

    assert "Due in 3 Days" in names
    assert "Due in 10 Days (outside window)" not in names
    assert len(data) == 1

def test_reminders_upcoming_endpoint_empty(client, jwt):
    response = client.get("/reminders/upcoming?days=7", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json == []