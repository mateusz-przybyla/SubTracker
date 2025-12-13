import pytest

from api.tasks.report_tasks import generate_monthly_report

@pytest.fixture
def mocked_dependencies(mocker):
    """
    Provides patched versions of task dependencies:
    - get_monthly_summary
    - send_monthly_summary_email
    - get_all_users
    """
    mock_get = mocker.patch("api.services.subscription.get_monthly_summary")
    mock_send = mocker.patch("api.tasks.email_tasks.send_monthly_summary_email")
    mock_users = mocker.patch("api.services.user.get_all_users")

    return mock_get, mock_send, mock_users

def test_generate_monthly_report_sends_email(mocker, mocked_dependencies):
    mock_get, mock_send, mock_users = mocked_dependencies

    mock_users.return_value = [mocker.Mock(id=1, email="test@example.com")]
    mock_get.return_value = {
        "month": "2025-11",
        "total_spent": 120,
        "by_category": {"Streaming": 60},
    }

    generate_monthly_report()

    mock_send.assert_called_once_with(
        user_email="test@example.com",
        summary=mock_get.return_value
    )

def test_generate_monthly_report_handles_no_data(mocker, mocked_dependencies):
    mock_get, mock_send, mock_users = mocked_dependencies

    mock_users.return_value = [mocker.Mock(id=1, email="test@example.com")]
    mock_get.return_value = {"month": "2025-11", "total_spent": 0, "by_category": {}}

    generate_monthly_report()

    mock_send.assert_not_called()

def test_generate_monthly_report_continues_on_error(mocker, mocked_dependencies):
    mock_get, mock_send, mock_users = mocked_dependencies

    mock_users.return_value = [
        mocker.Mock(id=1, email="u1@example.com"), 
        mocker.Mock(id=2, email="u2@example.com")
    ]

    mock_get.return_value = {"month": "2025-11", "total_spent": 50, "by_category": {}}
    mock_send.side_effect = [Exception("Email fail"), True]

    generate_monthly_report()

    assert mock_send.call_count == 2  # still attempts for user2

def test_generate_monthly_report_multiple_users(mocker, mocked_dependencies):
    mock_get, mock_send, mock_users = mocked_dependencies

    mock_users.return_value = [
        mocker.Mock(id=1, email="u1@example.com"), 
        mocker.Mock(id=2, email="u2@example.com")
    ]

    mock_get.side_effect = [
        {"month": "2025-11", "total_spent": 0, "by_category": {}},
        {"month": "2025-11", "total_spent": 80, "by_category": {"Games": 80}},
    ]

    generate_monthly_report()

    mock_send.assert_called_once_with(
        user_email="u2@example.com",
        summary={"month": "2025-11", "total_spent": 80, "by_category": {"Games": 80}},
    )