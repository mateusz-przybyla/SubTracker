from datetime import date, timedelta
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from decimal import Decimal

from api.extensions import db
from api.models import SubscriptionModel
from api.exceptions import (
    SubscriptionNotFoundError, 
    SubscriptionCreateError, 
    SubscriptionUpdateError, 
    SubscriptionDeleteError, 
    SubscriptionExistError
)

def check_if_subscription_name_exists(user_id: int, name: str) -> None:
    if SubscriptionModel.query.filter_by(user_id=user_id, name=name).first():
        raise SubscriptionExistError("You already have a subscription with this name.")

def check_if_subscription_exists(sub_id: int, user_id: int) -> SubscriptionModel:
    subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
    if not subscription:
        raise SubscriptionNotFoundError("Subscription not found.")
    return subscription

def create_subscription(data: dict, user_id: int) -> SubscriptionModel:
    check_if_subscription_name_exists(user_id, data['name'])

    subscription = SubscriptionModel(**data, user_id=user_id)
    try:
        db.session.add(subscription)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise SubscriptionCreateError("An error occurred while creating the subscription.")

    return subscription
  
def get_user_subscriptions(user_id: int) -> List[SubscriptionModel]:
    return SubscriptionModel.query.filter_by(user_id=user_id).all()

def get_user_subscription_by_id(sub_id: int, user_id: int) -> SubscriptionModel:
    return check_if_subscription_exists(sub_id, user_id)

def update_subscription(sub_id: int, user_id: int, data: dict) -> SubscriptionModel:
    subscription = check_if_subscription_exists(sub_id, user_id)

    if "name" in data and data['name'] != subscription.name:
        check_if_subscription_name_exists(user_id, data['name'])

    for key, value in data.items():
        setattr(subscription, key, value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise SubscriptionUpdateError("An error occurred while updating the subscription.")

    return subscription

def delete_subscription(sub_id: int, user_id: int) -> None:
    subscription = check_if_subscription_exists(sub_id, user_id)
    
    try:
        db.session.delete(subscription)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise SubscriptionDeleteError("An error occurred while deleting the subscription.")

def get_subscriptions_due_in(days_list: list[int]) -> List[SubscriptionModel]:
    """
    Retrieve subscriptions with next_payment_date exactly N days from today.

    Args:
        days_list (List[int]): List of day offsets from today.
            Example: [1, 7] → returns subscriptions due tomorrow or in 7 days.

    Returns:
        List[SubscriptionModel]: Subscriptions matching the given offsets.
    """
    today = date.today()
    target_dates = [today + timedelta(days=d) for d in days_list]

    return (
        SubscriptionModel.query
        .filter(SubscriptionModel.next_payment_date.in_(target_dates))
        .all()
    )

def get_user_upcoming_subscriptions(
    user_id: int,
    days_list: List[int] | None = None
) -> List[SubscriptionModel]:
    """
    Retrieve subscriptions for a specific user that have a next_payment_date
    exactly N days from today.

    Args:
        user_id (int): ID of the user whose subscriptions should be retrieved.
        days_list (List[int] | None): List of day offsets from today to check.
            Example: [1, 7] → returns subscriptions due tomorrow or in 7 days.
            Defaults to [1, 7].

    Returns:
        List[SubscriptionModel]: List of upcoming subscriptions for the user.
    """
    if days_list is None:
        days_list = [1, 7]

    today = date.today()
    target_dates = [today + timedelta(days=d) for d in days_list]

    return (
        SubscriptionModel.query
        .filter(SubscriptionModel.user_id == user_id)
        .filter(SubscriptionModel.next_payment_date.in_(target_dates))
        .all()
    )

def get_user_upcoming_within(user_id: int, days: int) -> List[SubscriptionModel]:
    """
    Retrieve all subscriptions for a specific user that have a next_payment_date
    within the given number of days from today.

    Args:
        user_id (int): ID of the user whose subscriptions should be retrieved.
        days (int): Number of days ahead to include in the search.
            Example: days=7 → returns subscriptions due today through the 
            next 7 days.

    Returns:
        List[SubscriptionModel]: List of SubscriptionModel objects representing
        upcoming payments for the user within the specified time window.
    """
    today = date.today()
    end_date = today + timedelta(days=days)

    return (
        SubscriptionModel.query
        .filter(SubscriptionModel.user_id == user_id)
        .filter(SubscriptionModel.next_payment_date.between(today, end_date))
        .all()
    )

def get_monthly_summary(user_id: int, month: str | None = None) -> dict[str, object]:
    """
    Calculate monthly spending summary for a given user.

    Args:
        user_id (int): ID of the user whose subscriptions are aggregated.
        month (str, optional): Month in YYYY-MM format. Defaults to current month.

    Returns:
        dict[str, object]: Summary with keys 'month', 'total_spent', 'by_category'.
    """
    if month is None:
        month = date.today().strftime("%Y-%m")

    year, month_num = map(int, month.split("-"))
    start_date = date(year, month_num, 1)
    if month_num == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month_num + 1, 1)

    subs = (
        SubscriptionModel.query
        .filter(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.next_payment_date >= start_date,
            SubscriptionModel.next_payment_date < end_date,
        )
        .all()
    )

    total_spent = Decimal("0.00")
    by_category: dict[str, float] = {}

    for sub in subs:
        try:
            amount = Decimal(sub.price)
        except ValueError:
            continue  # skip if the price is not a number

        total_spent += amount
        category = sub.category or "uncategorized"
        by_category[category] = by_category.get(category, Decimal("0.00")) + amount

    return {
        "month": month,
        "total_spent": float(round(total_spent, 2)),
        "by_category": {k: float(round(v, 2)) for k, v in by_category.items()},
    }

def get_subscription_by_id(sub_id: int) -> SubscriptionModel:
    subscription = SubscriptionModel.query.get(sub_id)
    if not subscription:
        raise SubscriptionNotFoundError("Subscription not found.")
    return subscription