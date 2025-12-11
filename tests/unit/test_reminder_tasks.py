import pytest
from datetime import date, timedelta

from api.tasks.reminder_tasks import check_upcoming_payments

@pytest.fixture
def mocked_dependencies(mocker):
    """
    Provides patched versions of task dependencies:
    - get_subscriptions_due_in
    - send_email_reminder
    - create_reminder_log
    """
    mock_get = mocker.patch("api.tasks.reminder_tasks.get_subscriptions_due_in")
    mock_send = mocker.patch("api.tasks.reminder_tasks.send_email_reminder")
    mock_log = mocker.patch("api.tasks.reminder_tasks.create_reminder_log")

    return mock_get, mock_send, mock_log

def make_sub_mock(mocker, sub_id, name, email, next_payment_date):
    sub = mocker.Mock()
    sub.id = sub_id
    sub.name = name
    sub.next_payment_date = next_payment_date
    sub.user = mocker.Mock(email=email)
    return sub

def test_check_upcoming_payments_processes_subscriptions(mocker, mocked_dependencies):
    mock_get, mock_send, mock_log = mocked_dependencies

    today = date.today()

    sub1 = make_sub_mock(mocker, 1, "Netflix", "test@example.com", today + timedelta(days=1))
    sub2 = make_sub_mock(mocker, 2, "Spotify", "another@example.com", today + timedelta(days=7))

    mock_get.return_value = [sub1, sub2]

    check_upcoming_payments()

    mock_get.assert_called_once_with([1, 7])
    assert mock_send.call_count == 2
    assert mock_log.call_count == 2

    mock_send.assert_any_call(
        user_email="test@example.com",
        subscription_name="Netflix",
        next_payment_date=sub1.next_payment_date,
    )
    mock_send.assert_any_call(
        user_email="another@example.com",
        subscription_name="Spotify",
        next_payment_date=sub2.next_payment_date,
    )

    mock_log.assert_any_call(
        sub_id=1,
        data={"message": "Reminder sent for Netflix", "success": True},
    )
    mock_log.assert_any_call(
        sub_id=2,
        data={"message": "Reminder sent for Spotify", "success": True},
    )

def test_check_upcoming_payments_handles_send_error(mocker, mocked_dependencies):
    mock_get, mock_send, mock_log = mocked_dependencies

    today = date.today()

    sub1 = make_sub_mock(mocker, 1, "good_sub", "good@example.com", today + timedelta(days=1))
    sub2 = make_sub_mock(mocker, 2, "bad_sub", "bad@example.com", today + timedelta(days=1))

    mock_get.return_value = [sub1, sub2]
    mock_send.side_effect = [True, Exception("Mail error")]

    check_upcoming_payments()

    assert mock_send.call_count == 2
    assert mock_log.call_count == 2

    mock_log.assert_any_call(
        sub_id=1,
        data={"message": "Reminder sent for good_sub", "success": True},
    )
    mock_log.assert_any_call(
        sub_id=2,
        data={"message": "Mail error", "success": False},
    )

def test_check_upcoming_payments_no_subscriptions(mocked_dependencies):
    mock_get, mock_send, mock_log = mocked_dependencies

    mock_get.return_value = []

    check_upcoming_payments()

    mock_send.assert_not_called()
    mock_log.assert_not_called()