from api.models import ReminderLogModel

def test_get_reminder_logs_by_subscription(client, db_session, jwt, sample_subscription):
    log1 = ReminderLogModel(message="Reminder log 1", success=True, subscription_id=sample_subscription.id)
    log2 = ReminderLogModel(message="Reminder log 2", success=False, subscription_id=sample_subscription.id)
    db_session.add_all([log1, log2])
    db_session.commit()

    response = client.get(f"/subscriptions/{sample_subscription.id}/reminder_logs", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert len(response.json) == 2
    messages = [log['message'] for log in response.json]
    assert "Reminder log 1" in messages
    assert "Reminder log 2" in messages

def test_get_reminder_logs_by_subscription_empty(client, jwt, sample_subscription):
    response = client.get(f"/subscriptions/{sample_subscription.id}/reminder_logs", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json == []

def test_get_reminder_logs_by_subscription_not_found(client, jwt):
    response = client.get("/subscriptions/999/reminder_logs", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Subscription not found."

def test_get_single_reminder_log(client, db_session, jwt, sample_subscription):
    log = ReminderLogModel(message="Single reminder log", success=True, subscription_id=sample_subscription.id)
    db_session.add(log)
    db_session.commit()

    response = client.get(f"/reminder_logs/{log.id}", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json['message'] == "Single reminder log"
    assert response.json['success'] is True

def test_get_single_reminder_log_not_found(client, jwt):
    response = client.get("/reminder_logs/999", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Reminder log not found."

def test_delete_reminder_log_success(client, db_session, jwt, sample_subscription):
    log = ReminderLogModel(message="Log to be deleted.", success=True, subscription_id=sample_subscription.id)
    db_session.add(log)
    db_session.commit()

    response = client.delete(f"/reminder_logs/{log.id}", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 200
    assert response.json['message'] == "Reminder log deleted."

    deleted_log = db_session.get(ReminderLogModel, log.id)
    assert deleted_log is None

def test_delete_reminder_log_not_found(client, jwt):
    response = client.delete("/reminder_logs/999", headers={"Authorization": f"Bearer {jwt}"})

    assert response.status_code == 404
    assert response.json['message'] == "Reminder log not found."