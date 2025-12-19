import pytest
import fakeredis
from datetime import date
from rq import Queue

from api.models import UserModel, SubscriptionModel, ReminderLogModel
from api.models.enums import BillingCycleEnum
from api.tasks import reminder_tasks
from api.exceptions import SubscriptionNotFoundError

@pytest.fixture
def fake_redis_conn():
    return fakeredis.FakeRedis()

@pytest.fixture
def reminder_queue(fake_redis_conn):
    return Queue("reminders", connection=fake_redis_conn)

@pytest.fixture
def mock_reminder_queue(mocker, reminder_queue):
    mocker.patch(
        "api.tasks.reminder_tasks.get_reminder_queue",
        return_value=reminder_queue
    )
    return reminder_queue

@pytest.fixture
def user_factory(db_session):
    def _factory(email):
        user = UserModel(username="user", email=email, password="secret")
        db_session.add(user)
        db_session.commit()
        return user
    return _factory

@pytest.fixture
def subscription_factory(db_session):
    def _factory(user_id, next_payment_date, name="Netflix"):
        sub = SubscriptionModel(
            name=name,
            price=29,
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=next_payment_date,
            category="Entertainment",
            user_id=user_id
        )
        db_session.add(sub)
        db_session.commit()
        return sub
    return _factory

def test_check_upcoming_payments_enqueues_job_per_subscription(
    app,
    mock_reminder_queue,
    user_factory,
    subscription_factory,
    mocker
):
    """
    Verifies that `check_upcoming_payments` enqueues exactly one reminder job
    per subscription with an upcoming payment.
    """
    user = user_factory(email="user@example.com")

    sub1 = subscription_factory(user.id, date(2025, 11, 10), name="Hulu")
    sub2 = subscription_factory(user.id, date(2025, 11, 11), name="Disney+")

    mocker.patch(
        "api.tasks.reminder_tasks.subscription_service.get_subscriptions_due_in",
        return_value=[sub1, sub2]
    )

    reminder_tasks.check_upcoming_payments(app=app)

    assert mock_reminder_queue.count == 2

    job = mock_reminder_queue.jobs[0]
    assert job.func_name.endswith("send_single_subscription_reminder")

def test_send_single_subscription_reminder_sends_email_and_logs_success(
    app,
    user_factory,
    subscription_factory,
    mocker
):
    user = user_factory(email="user@example.com")
    sub = subscription_factory(user.id, date(2025, 11, 10))

    mock_send = mocker.patch(
        "api.tasks.reminder_tasks.email_tasks.send_email_reminder"
    )

    reminder_tasks.send_single_subscription_reminder(
        sub_id=sub.id,
        app=app
    )

    mock_send.assert_called_once_with(
        user_email=user.email,
        subscription_name=sub.name,
        next_payment_date=sub.next_payment_date,
    )
    logs = ReminderLogModel.query.all()
    assert len(logs) == 1
    assert logs[0].subscription_id == sub.id
    assert logs[0].success is True

def test_send_single_subscription_reminder_skips_when_subscription_not_found(
    app,
    mocker
):
    mocker.patch(
        "api.tasks.reminder_tasks.subscription_service.get_subscription_by_id",
        side_effect=SubscriptionNotFoundError("Subscription not found")
    )

    mock_send = mocker.patch(
        "api.tasks.reminder_tasks.email_tasks.send_email_reminder"
    )

    reminder_tasks.send_single_subscription_reminder(
        sub_id=999,
        app=app
    )

    mock_send.assert_not_called()
    logs = ReminderLogModel.query.all()
    assert len(logs) == 0