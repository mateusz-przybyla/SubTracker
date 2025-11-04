from api.models import SubscriptionModel
from api.extensions import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_smorest import abort

def create_subscription(data, user_id):
    subscription = SubscriptionModel(**data, user_id=user_id)
    try:
        db.session.add(subscription)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, message="Subscription data violates a database constraint.")
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while creating the subscription.")

    return subscription

def get_user_subscriptions(user_id):
    try:
        return SubscriptionModel.query.filter_by(user_id=user_id).all()
    except SQLAlchemyError:
        abort(500, message="An error occurred while fetching subscriptions.")

def get_subscription_by_id(sub_id, user_id):
    try:
        subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
        if not subscription:
            abort(404, message="Subscription not found.")
        return subscription
    except SQLAlchemyError:
        abort(500, message="An error occurred while fetching the subscription.")

def update_subscription(sub_id, user_id, data):
    try:
        subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
        if not subscription:
            abort(404, message="Subscription not found.")

        for key, value in data.items():
            setattr(subscription, key, value)

        db.session.commit()
        return subscription
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while updating the subscription.")

def delete_subscription(sub_id, user_id):
    try:
        subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
        if not subscription:
            abort(404, message="Subscription not found.")
        db.session.delete(subscription)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while deleting the subscription.")
