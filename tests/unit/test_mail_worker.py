from datetime import date

from workers.mail_worker import send_email_reminder, send_user_registration_email

def test_send_user_registration_email_calls_mailgun_and_renders_template(mocker):
    mock_render = mocker.patch("workers.mail_worker.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("workers.mail_worker.send_mailgun_message", return_value="OK")

    result = send_user_registration_email("test@example.com", "test_user")

    # checking template rendering    
    mock_render.assert_called_once_with(
        "email/registration.html", 
        username="test_user")
    # checking mailgun call
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Successfully signed up",
        body="Hi test_user, you have successfully signed up for our service!",
        html="<html>"
    )
    assert result == "OK"
    
def test_send_email_reminder_calls_mailgun_and_renders_template(mocker):
    mock_render = mocker.patch("workers.mail_worker.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("workers.mail_worker.send_mailgun_message", return_value="OK")

    result = send_email_reminder("test@example.com", "Netflix", date(2025, 1, 1))

    # checking template rendering
    mock_render.assert_called_once_with(
        "email/reminder.html",
        subscription_name="Netflix",
        next_payment_date="2025-01-01",
    )
    # checking mailgun call
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Upcoming payment reminder: Netflix",
        body="Your next payment for Netflix is due on 2025-01-01.",
        html="<html>"
    )
    assert result == "OK"