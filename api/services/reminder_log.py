from sqlalchemy.exc import SQLAlchemyError
from typing import List

from api.extensions import db
from api.models import ReminderLogModel
from api.services import subscription as subscription_service
from api.exceptions import ReminderLogNotFoundError, ReminderLogDeleteError, ReminderLogCreateError

def check_if_reminder_log_exists(log_id: int) -> ReminderLogModel:
    reminder_log = ReminderLogModel.query.filter_by(id=log_id).first()
    if not reminder_log:
        raise ReminderLogNotFoundError("Reminder log not found.")
    return reminder_log

def create_reminder_log(data: dict, sub_id: int) -> ReminderLogModel:
    reminder_log = ReminderLogModel(**data, subscription_id=sub_id)
    
    try:
        db.session.add(reminder_log)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ReminderLogCreateError("An error occurred while creating the reminder log.")
    
    return reminder_log

def get_reminder_logs_by_subscription(sub_id: int, user_id: int) -> List[ReminderLogModel]:
    subscription_service.get_user_subscription_by_id(sub_id, user_id)
    return ReminderLogModel.query.filter_by(subscription_id=sub_id).all()

def get_reminder_log_by_id(log_id: int) -> ReminderLogModel:
    return check_if_reminder_log_exists(log_id)

def delete_reminder_log(log_id: int) -> None:
    reminder_log = check_if_reminder_log_exists(log_id)
    
    try:
        db.session.delete(reminder_log)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ReminderLogDeleteError("An error occurred while deleting the reminder log.")