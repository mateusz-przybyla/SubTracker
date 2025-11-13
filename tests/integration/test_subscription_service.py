import pytest
import datetime
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
        "next_payment_date": datetime.date(2025, 2, 10),
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
        "next_payment_date": datetime.date(2025, 3, 1),
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
        next_payment_date=datetime.date(2025, 4, 1),
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
        "next_payment_date": datetime.date(2025, 5, 1),
    }

    mock_rollback = mocker.patch("api.services.subscription.db.session.rollback")

    with pytest.raises(Exception) as e:
        service.create_subscription(data, sample_user.id)
    
    mock_rollback.assert_called_once()
    assert e.value.code == 500