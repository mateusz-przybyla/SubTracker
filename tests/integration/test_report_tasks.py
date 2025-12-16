import pytest
import fakeredis
from decimal import Decimal
from datetime import date
from rq import Queue

from api.models import UserModel, SubscriptionModel
from api.models.enums import BillingCycleEnum
from api.tasks import report_tasks

@pytest.fixture
def fake_redis_conn():
    return fakeredis.FakeRedis()

@pytest.fixture
def report_queue(fake_redis_conn):
    return Queue("reports", connection=fake_redis_conn)

@pytest.fixture
def mock_report_queue(mocker, report_queue):
    mocker.patch(
        "api.tasks.report_tasks.get_report_queue",
        return_value=report_queue
    )
    return report_queue

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
    def _factory(user_id, next_payment_date):
        subscription = SubscriptionModel(
            name="Netflix",
            price=Decimal("29.99"),
            billing_cycle=BillingCycleEnum.monthly,
            next_payment_date=next_payment_date,
            category="Entertainment",
            user_id=user_id
        )
        db_session.add(subscription)
        db_session.commit()
        return subscription
    return _factory

def test_generate_monthly_report_enqueues_job_per_user(
    app,
    mock_report_queue,
    user_factory
):
    """
    Verifies that `generate_monthly_report` enqueues exactly one background job
    per existing user.

    Fixtures used:
    - app: Flask application context required by the task
    - mock_report_queue: a real RQ Queue backed by FakeRedis, injected into the task
      via `get_report_queue` patching
    - user_factory: creates persisted users in the test database

    The test ensures that:
    - a job is enqueued for each user
    - the enqueued job targets `send_single_user_monthly_report`
    """
    user_factory(email="user1@example.com")
    user_factory(email="user2@example.com")

    report_tasks.generate_monthly_report(app=app)

    assert mock_report_queue.count == 2

    job = mock_report_queue.jobs[0]
    assert job.func_name.endswith("send_single_user_monthly_report")

def test_send_single_user_monthly_report_sends_email(
    app,
    user_factory,
    subscription_factory,
    mocker
):
    user = user_factory(email="user@example.com")
    subscription_factory(
        user_id=user.id,
        next_payment_date=date(2025, 11, 5)
    )

    mock_send = mocker.patch(
        "api.tasks.email_tasks.send_monthly_summary_email"
    )

    report_tasks.send_single_user_monthly_report(
        user_id=user.id,
        month="2025-11",
        app=app
    )

    mock_send.assert_called_once()

def test_send_single_user_monthly_report_skips_when_no_subscriptions(
    app,
    user_factory,
    mocker
):
    user = user_factory(email="user@example.com")

    mock_send = mocker.patch(
        "api.tasks.email_tasks.send_monthly_summary_email"
    )

    report_tasks.send_single_user_monthly_report(
        user_id=user.id,
        month="2025-11",
        app=app
    )

    mock_send.assert_not_called()

def test_send_single_user_monthly_report_does_not_crash_on_email_error(
    app,
    user_factory,
    subscription_factory,
    mocker
):
    user = user_factory(email="user@example.com")
    subscription_factory(
        user_id=user.id,
        next_payment_date=date(2025, 11, 10)
    )

    mocker.patch(
        "api.tasks.email_tasks.send_monthly_summary_email",
        side_effect=Exception("Email sending failed")
    )

    # Act + Assert: Should not raise
    report_tasks.send_single_user_monthly_report(
        user_id=user.id,
        month="2025-11",
        app=app
    )