from datetime import date, timedelta
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError

from api.models import SubscriptionModel
from api.extensions import db

def create_subscription(data, user_id):
    if SubscriptionModel.query.filter_by(user_id=user_id, name=data['name']).first():
        abort(409, message="You already have a subscription with this name.")

    subscription = SubscriptionModel(**data, user_id=user_id)
    try:
        db.session.add(subscription)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while creating the subscription.")

    return subscription

def get_user_subscriptions(user_id):
    return SubscriptionModel.query.filter_by(user_id=user_id).all()

def get_subscription_by_id(sub_id, user_id):
    subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
    if not subscription:
        abort(404, message="Subscription not found.")

    return subscription

def update_subscription(sub_id, user_id, data):
    subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
    if not subscription:
        abort(404, message="Subscription not found.")

    if "name" in data and data['name'] != subscription.name:
        if SubscriptionModel.query.filter_by(user_id=user_id, name=data['name']).first():
            abort(409, message="You already have a subscription with this name.")

    for key, value in data.items():
        setattr(subscription, key, value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while updating the subscription.")

    return subscription

def delete_subscription(sub_id, user_id):
    subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
    if not subscription:
        abort(404, message="Subscription not found.")
    
    try:
        db.session.delete(subscription)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while deleting the subscription.")

def get_subscriptions_due_in(days_list):
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