import pytest

from api.services import reminder_log as service
from api.models import ReminderLogModel

def test_create_reminder_log_success(sample_subscription):
    data = {
        "message": "We will charge you in 3 days.",
        "success": True
    }

    result = service.create_reminder_log(data, sample_subscription.id)
    assert result.id is not None
    assert result.message == "We will charge you in 3 days."

    saved = ReminderLogModel.query.filter_by(subscription_id=sample_subscription.id).first()
    assert saved is not None

def test_get_reminder_logs_by_subscription(db_session, sample_subscription):
    log1 = ReminderLogModel(message="Reminder log 1", success=True, subscription_id=sample_subscription.id)
    log2 = ReminderLogModel(message="Reminder log 2", success=False, subscription_id=sample_subscription.id)

    db_session.add_all([log1, log2])
    db_session.commit()

    results = service.get_reminder_logs_by_subscription(sample_subscription.id, sample_subscription.user_id)
    assert len(results) == 2
    messages = [log.message for log in results]
    assert "Reminder log 1" in messages
    assert "Reminder log 2" in messages

def test_get_reminder_logs_by_subscription_empty(sample_subscription):
    results = service.get_reminder_logs_by_subscription(sample_subscription.id, sample_subscription.user_id)
    assert results == []

def test_get_reminder_logs_by_subscription_not_found(sample_user):
    with pytest.raises(Exception) as e:
        service.get_reminder_logs_by_subscription(999, sample_user.id)

    assert e.value.code == 404

def test_get_single_reminder_log(db_session, sample_subscription):
    log = ReminderLogModel(message="Single log", success=True, subscription_id=sample_subscription.id)
    db_session.add(log)
    db_session.commit()

    result = service.get_reminder_log_by_id(log.id)
    assert result.message == "Single log"

def test_get_single_reminder_log_not_found():
    with pytest.raises(Exception) as e:
        service.get_reminder_log_by_id(999)

    assert e.value.code == 404

def test_delete_reminder_log_success(db_session, sample_subscription):
    log = ReminderLogModel(message="Log to be deleted.", success=True, subscription_id=sample_subscription.id)
    db_session.add(log)
    db_session.commit()

    service.delete_reminder_log(log.id)

    deleted_log = db_session.get(ReminderLogModel, log.id)
    assert deleted_log is None

def test_delete_reminder_log_not_found():
    with pytest.raises(Exception) as e:
        service.delete_reminder_log(999)

    assert e.value.code == 404