import pytest
from datetime import timedelta, date
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from api.models import SubscriptionModel
from api.models.enums import BillingCycleEnum
from api.services import subscription as service
from api.exceptions import (
    SubscriptionExistError,
    SubscriptionNotFoundError,
    SubscriptionCreateError
)

def test_create_subscription_success(sample_user):
    data = {
        "name": "Spotify",
        "price": Decimal("19.99"),
        "billing_cycle": BillingCycleEnum.monthly,
        "next_payment_date": date(2025, 2, 10),
        "category": "music"
    }

    result = service.create_subscription(data, sample_user.id)
    assert result.id is not None
    assert result.name == "Spotify"

    saved = SubscriptionModel.query.filter_by(user_id=sample_user.id, name="Spotify").first()
    assert saved is not None

def test_create_subscription_duplicate_name(sample_user, sample_subscription):
    data = {
        "name": sample_subscription.name,
        "price": Decimal("25.00"),
        "billing_cycle": BillingCycleEnum.monthly,
        "next_payment_date": date(2025, 3, 1),
        "category": "entertainment"
    }

    with pytest.raises(SubscriptionExistError) as exc_info:
        service.create_subscription(data, sample_user.id)

    assert str(exc_info.value) == "You already have a subscription with this name."

def test_get_user_subscriptions(sample_user, sample_subscription):
    results = service.get_user_subscriptions(sample_user.id)
    assert len(results) == 1
    assert results[0].name == "Netflix"

def test_get_user_subscriptions_empty(sample_user):
    results = service.get_user_subscriptions(sample_user.id)
    assert results == []

def test_get_subscription_by_id_success(sample_user, sample_subscription):
    result = service.get_user_subscription_by_id(sample_subscription.id, sample_user.id)
    assert result.name == "Netflix"

def test_get_subscription_by_id_not_found(sample_user):
    with pytest.raises(SubscriptionNotFoundError) as exc_info:
        service.get_user_subscription_by_id(999, sample_user.id)

    assert str(exc_info.value) == "Subscription not found."

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
        category="entertainment",
        user_id=sample_user.id,
    )
    db_session.add(another_subscription)
    db_session.commit()

    data = {"name": "Hulu"}

    with pytest.raises(SubscriptionExistError) as exc_info:
        service.update_subscription(sample_subscription.id, sample_user.id, data)

    assert str(exc_info.value) == "You already have a subscription with this name."

def test_update_subscription_not_found(sample_user):
    data = {"price": Decimal("49.99")}

    with pytest.raises(SubscriptionNotFoundError) as exc_info:
        service.update_subscription(999, sample_user.id, data)

    assert str(exc_info.value) == "Subscription not found."

def test_delete_subscription_success(db_session, sample_user, sample_subscription):
    service.delete_subscription(sample_subscription.id, sample_user.id)
    
    deleted_sub = db_session.get(SubscriptionModel, sample_subscription.id)
    assert deleted_sub is None

def test_delete_subscription_not_found(sample_user):
    with pytest.raises(SubscriptionNotFoundError) as exc_info:
        service.delete_subscription(999, sample_user.id)

    assert str(exc_info.value) == "Subscription not found."

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
        "category": "entertainment"
    }

    mock_rollback = mocker.patch("api.services.subscription.db.session.rollback")

    with pytest.raises(SubscriptionCreateError) as exc_info:
        service.create_subscription(data, sample_user.id)
    
    mock_rollback.assert_called_once()
    assert str(exc_info.value) == "An error occurred while creating the subscription."

def test_get_subscriptions_due_in_filters_by_exact_days_list(db_session, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due Tomorrow",
            price=Decimal("19.99"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=1),
            category="music"
        ),
        SubscriptionModel(
            user_id=sample_user.id + 3,  # Different user
            name="Due Tomorrow",
            price=Decimal("12.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=1),
            category="news"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 7 Days",
            price=Decimal("9.99"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=7),
            category="video"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 3 Days",
            price=Decimal("5.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=3),
            category="books"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Already Paid",
            price=Decimal("12.00"),
            billing_cycle=BillingCycleEnum.monthly,
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

def test_get_user_upcoming_within_returns_only_user_subs(db_session, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due Today",
            price=Decimal("10.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today,
            category="music"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 5 Days",
            price=Decimal("15.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=5),
            category="video"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 10 Days (outside window)",
            price=Decimal("20.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=10),
            category="books"
        ),
        SubscriptionModel(
            user_id=sample_user.id + 1,  # Different user
            name="Other User Due Tomorrow",
            price=Decimal("12.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=1),
            category="news"
        ),
        SubscriptionModel(
            user_id=sample_user.id,
            name="Already Paid",
            price=Decimal("8.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today - timedelta(days=1),
            category="games"
        ),
    ]
    db_session.add_all(subs)
    db_session.commit()

    result = service.get_user_upcoming_within(sample_user.id, days=7)

    names = {sub.name for sub in result}
    assert "Due Today" in names
    assert "Due in 5 Days" in names
    assert "Due in 10 Days (outside window)" not in names
    assert "Other User Due Tomorrow" not in names
    assert "Already Paid" not in names
    assert len(result) == 2

def test_get_user_upcoming_within_returns_empty_when_no_matches(db_session, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due in 20 Days",
            price=Decimal("25.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=20),
            category="fitness"
        )
    ]
    db_session.add_all(subs)
    db_session.commit()

    result = service.get_user_upcoming_within(sample_user.id, days=7)
    assert result == [] or len(result) == 0

def test_get_user_upcoming_within_includes_boundary_day(db_session, sample_user):
    today = date.today()
    subs = [
        SubscriptionModel(
            user_id=sample_user.id,
            name="Due Exactly in 7 Days",
            price=Decimal("30.00"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=today + timedelta(days=7),
            category="education"
        )
    ]
    db_session.add_all(subs)
    db_session.commit()

    result = service.get_user_upcoming_within(sample_user.id, days=7)
    assert len(result) == 1
    assert result[0].name == "Due Exactly in 7 Days"

def test_get_monthly_summary_returns_correct_totals(db_session, sample_user):
    # Arrange: subs in October
    sub1 = SubscriptionModel(
        user_id=sample_user.id,
        name="Netflix",
        price=Decimal("29.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 10, 5),
        category="entertainment"
    )
    sub2 = SubscriptionModel(
        user_id=sample_user.id,
        name="Spotify",
        price=Decimal("22.47"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 10, 10),
        category="music"
    )
    sub3 = SubscriptionModel(
        user_id=sample_user.id,
        name="Notion",
        price=Decimal("19.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 10, 15),
        category="productivity"
    )
    sub4 = SubscriptionModel(
        user_id=sample_user.id,
        name="Disney+",
        price=Decimal("29.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 10, 5),
        category="entertainment" # entertainment x2
    )
    db_session.add_all([sub1, sub2, sub3, sub4])
    db_session.commit()

    # Act
    summary = service.get_monthly_summary(sample_user.id, "2025-10")

    # Assert
    assert summary['month'] == "2025-10"
    assert summary['total_spent'] == Decimal("102.44")
    assert summary['by_category'] == {
        "entertainment": Decimal("59.98"),
        "music": Decimal("22.47"),
        "productivity": Decimal("19.99")
    }

def test_get_monthly_summary_skips_other_months(db_session, sample_user):
    # Arrange: sub in November
    sub = SubscriptionModel(
        user_id=sample_user.id,
        name="Disney+",
        price=Decimal("10.00"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 11, 1),
        category="entertainment"
    )
    db_session.add(sub)
    db_session.commit()

    # Act
    summary = service.get_monthly_summary(sample_user.id, "2025-10")

    # Assert
    assert summary['month'] == "2025-10"
    assert summary['total_spent'] == Decimal("0.00")
    assert summary['by_category'] == {}

def test_get_monthly_summary_returns_zero_when_no_subscriptions(sample_user):
    summary = service.get_monthly_summary(sample_user.id, "2025-08")

    assert summary['month'] == "2025-08"
    assert summary['total_spent'] == Decimal("0.00")
    assert summary['by_category'] == {}

# legacy safety net
def test_get_monthly_summary_handles_missing_category(db_session, sample_user):
    # Arrange: uncategorized sub
    sub = SubscriptionModel(
        user_id=sample_user.id,
        name="VPN",
        price=Decimal("5.00"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=date(2025, 10, 20),
        category=None
    )
    db_session.add(sub)
    db_session.commit()

    # Act
    summary = service.get_monthly_summary(sample_user.id, "2025-10")

    # Assert: fallback on "uncategorized"
    assert summary['by_category'] == {"uncategorized": Decimal("5.00")}

def test_get_monthly_summary_rounds_to_two_decimal_places(sample_user, subscription_factory):
    subscription_factory(
        user_id=sample_user.id,
        price=Decimal("10.005"),
        category="test",
        next_payment_date=date(2025, 7, 1)
    )

    summary = service.get_monthly_summary(sample_user.id, "2025-07")

    assert summary['total_spent'] == Decimal("10.01")
    assert summary['by_category']['test'] == Decimal("10.01")