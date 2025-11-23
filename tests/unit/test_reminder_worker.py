import pytest
from datetime import date

from api.workers.reminder_worker import check_upcoming_payments

@pytest.fixture
def worker_mocks(mocker):
    """
    Provides patched versions of worker dependencies:
    - get_subscriptions_due_in
    - send_email_reminder
    - create_reminder_log
    """
    mock_get = mocker.patch("api.workers.reminder_worker.get_subscriptions_due_in")
    mock_send = mocker.patch("api.workers.reminder_worker.send_email_reminder")
    mock_log = mocker.patch("api.workers.reminder_worker.create_reminder_log")

    return mock_get, mock_send, mock_log

def test_check_upcoming_payments_processes_subscriptions(mocker, worker_mocks):
    # Mock dependencies
    mock_get, mock_send, mock_log = worker_mocks

    # Fake subscriptions
    sub1 = mocker.Mock()
    sub1.id = 1
    sub1.name = "Netflix"
    sub1.next_payment_date = date.today()
    sub1.user.email = "test@example.com"

    sub2 = mocker.Mock()
    sub2.id = 2
    sub2.name = "Spotify"
    sub2.next_payment_date = date.today()
    sub2.user.email = "another@example.com"

    mock_get.return_value = [sub1, sub2]

    # Run worker
    check_upcoming_payments()

    # Assertions
    assert mock_send.call_count == 2
    assert mock_log.call_count == 2

    mock_send.assert_any_call(
        user_email="test@example.com",
        subscription_name="Netflix",
        next_payment_date=sub1.next_payment_date,
    )

def test_check_upcoming_payments_handles_send_error(mocker, worker_mocks):
    # Mock dependencies
    mock_get, mock_send, mock_log = worker_mocks

    sub = mocker.Mock()
    sub.id = 123
    sub.name = "HBO"
    sub.next_payment_date = date.today()
    sub.user.email = "some@example.com"

    mock_get.return_value = [sub]
    mock_send.side_effect = Exception("Mail error")

    # Run worker
    check_upcoming_payments()

    # Assertions
    mock_send.assert_called_once()
    mock_log.assert_called_once()
    
    args, kwargs = mock_log.call_args
    assert kwargs['sub_id'] == 123
    assert kwargs['data']['success'] is False

def test_check_upcoming_payments_no_subscriptions(worker_mocks):
    # Mock dependencies
    mock_get, mock_send, mock_log = worker_mocks

    mock_get.return_value = []

    # Run worker
    check_upcoming_payments()

    # Assertions
    mock_send.assert_not_called()
    mock_log.assert_not_called()