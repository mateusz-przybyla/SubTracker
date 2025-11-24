import pytest
from datetime import timedelta, date
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from api.models import SubscriptionModel
from api.services import subscription as service
from api.models.enums import BillingCycleEnum

def test_create_subscription_success(sample_user):
    data = {
        "name": "Spotify",
        "price": Decimal("19.99"),
        "billing_cycle": BillingCycleEnum.monthly,
        "next_payment_date": date(2025, 2, 10),
    }

    result = service.create_subscription(data, sample_user.id)
    assert result.id is not None
    assert result.name == "Spotify"

    saved = SubscriptionModel.query.filter_by(user_id=sample_user.id, name="Spotify").first()
    assert saved is not None

def test_create_subscription_duplicate_name(sample_user, sample_subscription):
    data = {
        "name": "Netflix",
        "price": Decimal("25.00"),
        "billing_cycle": BillingCycleEnum.monthly,
        "next_payment_date": date(2025, 3, 1),
    }

    with pytest.raises(Exception) as e:
        service.create_subscription(data, sample_user.id)

    assert e.value.code == 409

def test_get_user_subscriptions(sample_user, sample_subscription):
    results = service.get_user_subscriptions(sample_user.id)
    assert len(results) == 1
    assert results[0].name == "Netflix"


def test_get_user_subscriptions_empty(sample_user):
    results = service.get_user_subscriptions(sample_user.id)
    assert results == []

def test_get_subscription_by_id_success(sample_user, sample_subscription):
    result = service.get_subscription_by_id(sample_subscription.id, sample_user.id)
    assert result.name == "Netflix"

def test_get_subscription_by_id_not_found(sample_user):
    with pytest.raises(Exception) as e:
        service.get_subscription_by_id(999, sample_user.id)

    assert e.value.code == 404

def test_update_subscription_success(db_session, sample_user, sample_subscription):
    data = {"price": Decimal("39.99")}
    result = service.update_subscription(sample_subscription.id, sample_user.id, data)

    assert result.price == Decimal("39.99")

    updated = db_session.get(SubscriptionModel, sample_subscription.id)
    assert updated.price == Decimal("39.99")

def test_update_subscription_rename_conflict(db_session, sample_user, sample_subscription):
    another_subscription = SubscriptionModel(
        name="Hulu",
        price=Decimal("14.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 4, 1),
        user_id=sample_user.id,
    )
    db_session.add(another_subscription)
    db_session.commit()

    data = {"name": "Hulu"}

    with pytest.raises(Exception) as e:
        service.update_subscription(sample_subscription.id, sample_user.id, data)

    assert e.value.code == 409

def test_update_subscription_not_found(sample_user):
    data = {"price": Decimal("49.99")}

    with pytest.raises(Exception) as e:
        service.update_subscription(999, sample_user.id, data)

    assert e.value.code == 404

def test_delete_subscription_success(db_session, sample_user, sample_subscription):
    service.delete_subscription(sample_subscription.id, sample_user.id)
    
    deleted_sub = db_session.get(SubscriptionModel, sample_subscription.id)
    assert deleted_sub is None


def test_delete_subscription_not_found(sample_user):
    with pytest.raises(Exception) as e:
        service.delete_subscription(999, sample_user.id)

    assert e.value.code == 404

def test_create_subscription_db_error(mocker, sample_user):
    mocker.patch(
        "api.services.subscription.db.session.add",
        side_effect=SQLAlchemyError("DB Error"),
    )

    data = {
        "name": "Disney+",
        "price": Decimal("12.99"),
        "billing_cycle": BillingCycleEnum.monthly,
        "next_payment_date": date(2025, 5, 1),
    }

    mock_rollback = mocker.patch("api.services.subscription.db.session.rollback")

    with pytest.raises(Exception) as e:
        service.create_subscription(data, sample_user.id)
    
    mock_rollback.assert_called_once()
    assert e.value.code == 500

def test_get_subscriptions_due_in_filters_by_exact_days_list(db_session, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due Tomorrow",
            price=19.99,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=1),
            category="music"
        ),
        SubscriptionModel(
            user_id=sample_user.id + 3,  # Different user
            name="Due Tomorrow",
            price=12.00,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=1),
            category="news"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 7 Days",
            price=9.99,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=7),
            category="video"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 3 Days",
            price=5.00,
            billing_cycle="monthly",
            next_payment_date=today + timedelta(days=3),
            category="books"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Already Paid",
            price=12.00,
            billing_cycle="monthly",
            next_payment_date=today - timedelta(days=1),
            category="news"
        ),
    ]
    db_session.add_all(subs)
    db_session.commit()

    result = service.get_subscriptions_due_in([1, 7])
    
    names = {sub.name for sub in result}
    assert "Due Tomorrow" in names
    assert "Due in 7 Days" in names
    assert "Due in 3 Days" not in names
    assert "Already Paid" not in names
    assert len(result) == 3

    dates = {sub.next_payment_date for sub in result}
    assert today + timedelta(days=1) in dates
    assert today + timedelta(days=7) in dates

def test_get_subscriptions_due_in_returns_empty_when_no_matches(db_session, sample_user):
    result = service.get_subscriptions_due_in([1, 7])
    assert result == [] or len(result) == 0