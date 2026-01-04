import os
import requests
import jinja2
from typing import Any
from datetime import date
from flask import current_app

from api.exceptions import EmailTemporaryError, EmailPermanentError

DOMAIN = os.getenv("MAILGUN_DOMAIN")
template_loader = jinja2.FileSystemLoader("api/templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename: str, **context: Any) -> str:
    """Render a Jinja2 template with the given context."""
    return template_env.get_template(template_filename).render(**context)
    
def send_mailgun_message(to: str, subject: str, body: str, html: str) -> None:
    """Send an email using the Mailgun API."""
    try:
        response = requests.post(
  	    f"https://api.mailgun.net/v3/{DOMAIN}/messages",
  		auth=("api", os.getenv("MAILGUN_API_KEY")),
  		data={"from": f"SubTracker Team <postmaster@{DOMAIN}>",
			"to": [to],
  			"subject": subject,
  			"text": body,
            "html": html,
        },
        timeout=(5, 10),
    )
    except requests.RequestException as e:
        raise EmailTemporaryError("Network error while sending email") from e
    
    if response.ok:
        return
    
    detail = response.text

    if response.status_code in {429, 500, 502, 503, 504}:
        raise EmailTemporaryError(
            f"Temporary Mailgun error {response.status_code}: {detail}"
        )

    if not response.ok:
        raise EmailPermanentError(
            f"Permanent Mailgun error {response.status_code}: {detail}"
        )

def send_user_registration_email(email: str, username: str) -> None:
    """Send a registration confirmation email to a new user."""
    try:
        send_mailgun_message(
            to=email,  
            subject="Successfully signed up",
            body=f"Hi {username}, you have successfully signed up for our service!",
            html=render_template("email/registration.html", username=username),
        )
    except EmailPermanentError as e:
        # Log the permanent error without retrying
        current_app.logger.error(
            "Permanent error sending registration email.",
            extra={"error": str(e), "user_email": email}
        )
        return
    except EmailTemporaryError as e:
        # Log the temporary error and raise to trigger a retry
        current_app.logger.warning(
            "Temporary error sending registration email.",
            extra={"error": str(e), "user_email": email}
        )
        raise

def send_email_reminder(user_email: str, subscription_name: str, next_payment_date: date) -> None:
    """Send an email reminder about an upcoming subscription payment."""
    formatted_date = next_payment_date.strftime("%Y-%m-%d")

    body = f"Your next payment for {subscription_name} is due on {formatted_date}."
    html = render_template(
        "email/reminder.html",
        subscription_name=subscription_name,
        next_payment_date=formatted_date,
    )

    send_mailgun_message(
        to=user_email,
        subject=f"Upcoming payment reminder: {subscription_name}",
        body=body,
        html=html,
    )

def send_monthly_summary_email(user_email: str, summary: dict[str, Any]) -> None:
    """Send a monthly subscription spending summary email to the user."""
    body = f"Your spending summary for {summary['month']} is {summary['total_spent']}."
    html = render_template(
        "email/monthly_summary.html",
        month=summary['month'],
        total_spent=summary['total_spent'],
        by_category=summary['by_category'],
    )

    send_mailgun_message(
        to=user_email,
        subject=f"Your subscription summary for {summary['month']}",
        body=body,
        html=html,
    )