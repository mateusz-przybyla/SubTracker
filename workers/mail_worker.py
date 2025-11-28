import os
import requests
import jinja2
from typing import Any
from datetime import date

DOMAIN = os.getenv("MAILGUN_DOMAIN")
template_loader = jinja2.FileSystemLoader("api/templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename: str, **context: Any) -> str:
    """Render a Jinja2 template with the given context."""
    return template_env.get_template(template_filename).render(**context)

def send_mailgun_message(to: str, subject: str, body: str, html: str) -> requests.Response:
    """Send an email using Mailgun API."""
    return requests.post(
  	    f"https://api.mailgun.net/v3/{DOMAIN}/messages",
  		auth=("api", os.getenv("MAILGUN_API_KEY")),
  		data={"from": f"Mateusz Przybyla <postmaster@{DOMAIN}>",
			"to": [to],
  			"subject": subject,
  			"text": body,
            "html": html 
        }
    )

def send_user_registration_email(email: str, username: str) -> requests.Response:
    """Send a registration confirmation email to a new user."""
    return send_mailgun_message(
        to=email,  
        subject="Successfully signed up",
        body=f"Hi {username}, you have successfully signed up for our service!",
        html=render_template("email/registration.html", username=username),
    )

def send_email_reminder(user_email: str, subscription_name: str, next_payment_date: date) -> requests.Response:
    """Send an email reminder about an upcoming subscription payment."""
    formatted_date = next_payment_date.strftime("%Y-%m-%d")

    body = f"Your next payment for {subscription_name} is due on {formatted_date}."
    html = render_template(
        "email/reminder.html",
        subscription_name=subscription_name,
        next_payment_date=formatted_date,
    )

    return send_mailgun_message(
        to=user_email,
        subject=f"Upcoming payment reminder: {subscription_name}",
        body=body,
        html=html,
    )