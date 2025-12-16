import pytest
from rq import Retry

from api.tasks import report_tasks

@pytest.fixture
def mocked_dependencies_1(mocker):
    """
    Provides patched versions of task dependencies for generate_monthly_report.
    """
    mock_users = mocker.patch("api.services.user.get_all_users")
    mock_queue = mocker.Mock()
    mocker.patch("api.tasks.report_tasks.get_report_queue", return_value=mock_queue)
    mock_month = mocker.patch(
        "api.tasks.report_tasks.date_helpers.get_previous_month",
        return_value="2025-11"
    )

    return mock_users, mock_queue, mock_month

@pytest.fixture
def mocked_dependencies_2(mocker):
    """
    Provides patched versions of task dependencies for send_single_user_monthly_report.
    """
    mock_summary = mocker.patch("api.services.subscription.get_monthly_summary")
    mock_get_user = mocker.patch("api.services.user.get_user_by_id")
    mock_send_email = mocker.patch("api.tasks.email_tasks.send_monthly_summary_email")

    return mock_summary, mock_get_user, mock_send_email

def test_generate_monthly_report_enqueues_job_per_user(mocker, mocked_dependencies_1):
    mock_users, mock_queue, _ = mocked_dependencies_1

    mock_users.return_value = [
        mocker.Mock(id=1),
        mocker.Mock(id=2),
    ]

    report_tasks.generate_monthly_report()

    assert mock_queue.enqueue.call_count == 2

def test_generate_monthly_report_enqueue_arguments(mocker, mocked_dependencies_1):
    mock_users, mock_queue, _ = mocked_dependencies_1

    user = mocker.Mock(id=42)
    mock_users.return_value = [user]

    report_tasks.generate_monthly_report()

    mock_queue.enqueue.assert_called_once()
    args, _ = mock_queue.enqueue.call_args

    assert args[0].__name__ == "send_single_user_monthly_report"
    assert args[1] == 42
    assert args[2] == "2025-11"

def test_generate_monthly_report_sets_retry_policy(mocker, mocked_dependencies_1):
    mock_users, mock_queue, _ = mocked_dependencies_1

    mock_users.return_value = [mocker.Mock(id=1)]

    report_tasks.generate_monthly_report()

    _, kwargs = mock_queue.enqueue.call_args
    retry = kwargs['retry']

    assert isinstance(retry, Retry)
    assert retry.max == 3

def test_send_single_user_monthly_report_sends_email(
    mocker,
    mocked_dependencies_2
):
    mock_summary, mock_get_user, mock_send_email = mocked_dependencies_2

    mock_summary.return_value = {
        "total_spent": 120,
        "by_category": {"Streaming": 120},
    }

    mock_get_user.return_value = mocker.Mock(
        email="test@example.com"
    )

    report_tasks.send_single_user_monthly_report(user_id=1, month="2025-11")

    mock_send_email.assert_called_once_with(
        user_email="test@example.com",
        summary=mock_summary.return_value,
    )

def test_send_single_user_monthly_report_skips_when_no_spending(
    mocked_dependencies_2
):
    mock_summary, mock_get_user, mock_send_email = mocked_dependencies_2

    mock_summary.return_value = {
        "total_spent": 0,
        "by_category": {},
    }

    report_tasks.send_single_user_monthly_report(
        user_id=1,
        month="2025-11"
    )

    mock_send_email.assert_not_called()
    mock_get_user.assert_not_called()

def test_send_single_user_monthly_report_handles_email_failure(
    mocker,
    mocked_dependencies_2
):
    mock_summary, mock_get_user, mock_send_email = mocked_dependencies_2

    mock_summary.return_value = {
        "total_spent": 30,
        "by_category": {},
    }

    mock_get_user.return_value = mocker.Mock(
        email="fail@example.com"
    )

    mock_send_email.side_effect = Exception("Email sending failed")

    # Act + Assert: Should not raise
    report_tasks.send_single_user_monthly_report(
        user_id=7,
        month="2025-11"
    )