from datetime import date, timedelta

from api.models import SubscriptionModel

def test_reminders_upcoming_endpoint_returns_subs(client, db_session, jwt, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 3 Days",
            price=9.99,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=3),
            category="video"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 10 Days (outside window)",
            price=12.00,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=10),
            category="books"
        ),
    ]
    db_session.add_all(subs)
    db_session.commit()

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