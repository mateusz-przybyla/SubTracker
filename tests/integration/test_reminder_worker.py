from datetime import timedelta, date

from api.models import SubscriptionModel, ReminderLogModel
from api.workers.reminder_worker import check_upcoming_payments

def test_check_upcoming_payments_sends_reminders(app, db_session, sample_user, mocker):
    today = date.today()

    # 2 subs matching criteria -> [1, 7] days
    sub1 = SubscriptionModel(
        user_id=sample_user.id,
        name="Sub1",
        price=19.99,
        billing_cycle="monthly",
        next_payment_date=today + timedelta(days=1),
        category="music"
    )
    sub2 = SubscriptionModel(
        user_id=sample_user.id,
        name="Sub2",
        price=19.99,
        billing_cycle="monthly",
        next_payment_date=today + timedelta(days=7),
        category="music"
    )
    # 1 sub not matching criteria -> 3 days
    sub3 = SubscriptionModel(
        user_id=sample_user.id,
        name="SkipSub",
        price=19.99,
        billing_cycle="monthly",
        next_payment_date=today + timedelta(days=3),
        category="music"
    )
    
    db_session.add_all([sub1, sub2, sub3])
    db_session.commit()

    # MOCK external side effects
    mock_send = mocker.patch(
        "api.workers.reminder_worker.send_email_reminder",
        return_value=True
    )

    # Run worker
    check_upcoming_payments(app=app)

    # assert mail was sent 2×
    assert mock_send.call_count == 2

    # assert reminder logs created
    logs = ReminderLogModel.query.order_by(ReminderLogModel.id).all()
    assert len(logs) == 2
    assert logs[0].subscription_id == sub1.id
    assert logs[0].success is True
    assert logs[1].subscription_id == sub2.id
    assert logs[1].success is True

def test_check_upcoming_payments_logs_error_on_send_failure(
        app, db_session, sample_user, mocker
):
    today = date.today()

    sub = SubscriptionModel(
        user_id=sample_user.id,
        name="BrokenSub",
        price=9.99,
        billing_cycle="monthly",
        next_payment_date=today + timedelta(days=1),
        category="tech"
    )

    db_session.add(sub)
    db_session.commit()

    # MOCK send_email_reminder to raise Exception
    mocker.patch(
        "api.workers.reminder_worker.send_email_reminder",
        side_effect=Exception("Email fail")
    )

    # Run worker
    check_upcoming_payments(app=app)

    logs = ReminderLogModel.query.all()
    assert len(logs) == 1
    assert logs[0].subscription_id == sub.id
    assert logs[0].success is False
    assert "Email fail" in logs[0].message