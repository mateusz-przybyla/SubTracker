import pytest
from datetime import date
from redis import RedisError

from api.tasks import reminder_tasks
from api.exceptions import SubscriptionNotFoundError, EmailTemporaryError, EmailPermanentError

@pytest.fixture
def mocked_dependencies_1(mocker):
    """
    Provides patched versions of task dependencies for `check_upcoming_payments`.
    """
    mock_get_subs = mocker.patch(
        "api.tasks.reminder_tasks.subscription_service.get_subscriptions_due_in"
    )
    mock_reminder_queue = mocker.Mock()
    mocker.patch(
        "api.tasks.reminder_tasks.get_reminder_queue", 
        return_value=mock_reminder_queue
    )

    return mock_get_subs, mock_reminder_queue

@pytest.fixture
def mocked_dependencies_2(mocker):
    """
    Provides patched versions of task dependencies for `send_single_subscription_reminder`.
    """
    mock_get_sub = mocker.patch(
        "api.tasks.reminder_tasks.subscription_service.get_subscription_by_id"
    )
    mock_send_email = mocker.patch(
        "api.tasks.reminder_tasks.email_tasks.send_email_reminder"
    )
    mock_create_log = mocker.patch(
        "api.tasks.reminder_tasks.reminder_log_service.create_reminder_log"
    )

    return mock_get_sub, mock_send_email, mock_create_log

def test_check_upcoming_payments_enqueues_job_per_subscription(
        app, 
        mocker, 
        mocked_dependencies_1
    ):  
    mock_get_subs, mock_reminder_queue = mocked_dependencies_1

    sub1 = mocker.Mock(id=1)
    sub2 = mocker.Mock(id=2)

    mock_get_subs.return_value = [sub1, sub2]

    reminder_tasks.check_upcoming_payments(app=app)

    assert mock_reminder_queue.enqueue.call_count == 2

def test_check_upcoming_payments_enqueue_arguments(
        app, 
        mocker, 
        mocked_dependencies_1
    ):
    mock_get_subs, mock_reminder_queue = mocked_dependencies_1

    sub = mocker.Mock(id=1)

    mock_get_subs.return_value = [sub]

    reminder_tasks.check_upcoming_payments(app=app)

    mock_reminder_queue.enqueue.assert_called_once()
    args, kwargs = mock_reminder_queue.enqueue.call_args

    assert args[0].__name__ == "send_single_subscription_reminder"
    assert args[1] == 1
    assert kwargs['retry'] is not None

def test_send_single_subscription_reminder_sends_email(
        app, 
        mocker, 
        mocked_dependencies_2
    ):
    mock_get_sub, mock_send_email, mock_create_log = mocked_dependencies_2

    sub = mocker.Mock()
    sub.id = 1
    sub.name = "Netflix"
    sub.next_payment_date = date(2025, 11, 10)
    sub.user = mocker.Mock(email="user@example.com")

    mock_get_sub.return_value = sub

    reminder_tasks.send_single_subscription_reminder(sub_id=1, app=app)

    mock_send_email.assert_called_once_with(
        user_email="user@example.com",
        subscription_name="Netflix",
        next_payment_date=date(2025, 11, 10)
    )
    mock_create_log.assert_called_once_with(
        data={"message": "Reminder sent for Netflix", "success": True},
        sub_id=1
    )

def test_send_single_subscription_reminder_skips_when_sub_not_found(
        app, 
        mocked_dependencies_2
    ):
    mock_get_sub, mock_send_email, mock_create_log = mocked_dependencies_2

    mock_get_sub.side_effect = SubscriptionNotFoundError()

    reminder_tasks.send_single_subscription_reminder(sub_id=999, app=app)

    mock_send_email.assert_not_called()
    mock_create_log.assert_not_called()

def test_send_single_subscription_reminder_handles_permanent_email_failure(
        app, 
        mocker, 
        mocked_dependencies_2
    ):
    mock_get_sub, mock_send_email, mock_create_log = mocked_dependencies_2

    sub = mocker.Mock()
    sub.id = 1
    sub.name = "Spotify"
    sub.next_payment_date = date(2025, 12, 1)
    sub.user = mocker.Mock(email="user@example.com")
    
    mock_get_sub.return_value = sub
    mock_send_email.side_effect = EmailPermanentError("Invalid email")

    reminder_tasks.send_single_subscription_reminder(sub_id=1, app=app)

    mock_send_email.assert_called_once_with(
        user_email="user@example.com",
        subscription_name="Spotify",
        next_payment_date=date(2025, 12, 1)
    )
    mock_create_log.assert_called_once_with(
        data={"message": "Invalid email", "success": False},
        sub_id=1
    )

def test_send_single_subscription_reminder_handles_temporary_email_failure(
        app, 
        mocker, 
        mocked_dependencies_2
    ):
    mock_get_sub, mock_send_email, mock_create_log = mocked_dependencies_2

    sub = mocker.Mock()
    sub.id = 1
    sub.name = "Spotify"
    sub.next_payment_date = date(2025, 12, 1)
    sub.user = mocker.Mock(email="user@example.com")
    
    mock_get_sub.return_value = sub
    mock_send_email.side_effect = EmailTemporaryError("Timeout occurred")

    with pytest.raises(EmailTemporaryError):
        reminder_tasks.send_single_subscription_reminder(sub_id=1, app=app)
    mock_create_log.assert_not_called()

def test_check_upcoming_payments_handles_redis_error(
    app,
    mocker,
    mocked_dependencies_1
):
    mock_get_subs, mock_reminder_queue = mocked_dependencies_1

    sub1 = mocker.Mock(id=1)
    sub2 = mocker.Mock(id=2)

    mock_get_subs.return_value = [sub1, sub2]

    mock_reminder_queue.enqueue.side_effect = RedisError("Redis down")

    # Act: should NOT raise
    reminder_tasks.check_upcoming_payments(app=app)