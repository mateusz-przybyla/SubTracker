from sqlalchemy.exc import SQLAlchemyError
from flask_smorest import abort

from api.models import ReminderLogModel, SubscriptionModel
from api.extensions import db

def create_reminder_log(data, sub_id):
    reminder_log = ReminderLogModel(**data, subscription_id=sub_id)
    
    try:
        db.session.add(reminder_log)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while creating the reminder log.")
    
    return reminder_log

def check_if_subscription_exists(sub_id, user_id):
    subscription = SubscriptionModel.query.filter_by(id=sub_id, user_id=user_id).first()
    if not subscription:
        abort(404, message="Subscription not found.")

def get_reminder_logs_by_subscription(sub_id, user_id):
    check_if_subscription_exists(sub_id, user_id)
    return ReminderLogModel.query.filter_by(subscription_id=sub_id).all()

def get_reminder_log_by_id(log_id):
    reminder_log = ReminderLogModel.query.filter_by(id=log_id).first()
    if not reminder_log:
        abort(404, message="Reminder log not found.")
    
    return reminder_log

def delete_reminder_log(log_id):
    reminder_log = ReminderLogModel.query.filter_by(id=log_id).first()
    if not reminder_log:
        abort(404, message="Reminder log not found.")
    
    try:
        db.session.delete(reminder_log)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while deleting the reminder log.")