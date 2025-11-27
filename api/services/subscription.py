from datetime import date, timedelta
from sqlalchemy.exc import SQLAlchemyError
from typing import List

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

def get_subscription_by_id(sub_id: int, user_id: int) -> SubscriptionModel:
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
    Retrieve subscriptions with next_payment_date in N days from today.
    Example: days_list = [1, 7] → returns subscriptions due tomorrow or in 7 days.
    """
    today = date.today()
    dates = [today + timedelta(days=d) for d in days_list]

    return (
        SubscriptionModel.query
        .filter(SubscriptionModel.next_payment_date.in_(dates))
        .all()
    )