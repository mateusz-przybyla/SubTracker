from datetime import date

from api.tasks import email_tasks

def test_registration_email_renders_and_sends(mocker):
    mock_render = mocker.patch("api.tasks.email_tasks.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("api.tasks.email_tasks.send_mailgun_message")

    email_tasks.send_user_registration_email("test@example.com", "test_user")
  
    mock_render.assert_called_once_with(
        "email/registration.html", 
        username="test_user")
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Successfully signed up",
        body="Hi test_user, you have successfully signed up for our service!",
        html="<html>"
    )
    
def test_reminder_email_renders_and_sends(mocker):
    mock_render = mocker.patch("api.tasks.email_tasks.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("api.tasks.email_tasks.send_mailgun_message")

    email_tasks.send_email_reminder("test@example.com", "Netflix", date(2025, 1, 1))

    mock_render.assert_called_once_with(
        "email/reminder.html",
        subscription_name="Netflix",
        next_payment_date="2025-01-01",
    )
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Upcoming payment reminder: Netflix",
        body="Your next payment for Netflix is due on 2025-01-01.",
        html="<html>"
    )

    mock_mailgun.assert_called_once()
    kwargs = mock_mailgun.call_args.kwargs

    assert kwargs['to'] == "test@example.com"
    assert kwargs['subject'] == "Upcoming payment reminder: Netflix"
    assert "Netflix" in kwargs['body']
    assert "2025-01-01" in kwargs['body']
    assert kwargs['html'] == "<html>"
   
def test_monthly_summary_email_renders_and_sends(mocker):
    mock_render = mocker.patch("api.tasks.email_tasks.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("api.tasks.email_tasks.send_mailgun_message")
    summary = {
        "month": "2025-10",
        "total_spent": 72.45,
        "by_category": {
            "entertainment": 29.99,
            "productivity": 19.99,
            "music": 22.47,
        },
    }

    email_tasks.send_monthly_summary_email("test@example.com", summary)

    mock_render.assert_called_once_with(
        "email/monthly_summary.html",
        month="2025-10",
        total_spent=72.45,
        by_category={
            "entertainment": 29.99,
            "productivity": 19.99,
            "music": 22.47,
        },
    )
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Your subscription summary for 2025-10",
        body="Your spending summary for 2025-10 is 72.45.",
        html="<html>",
    )