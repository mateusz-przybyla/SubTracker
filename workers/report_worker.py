from flask import Flask

from api.services.subscription import get_monthly_summary
from api.utils.validators import get_previous_month
from api.models import UserModel
from workers.mail_worker import send_monthly_summary_email

def generate_monthly_report(app: Flask | None = None) -> None:
    """
    Worker that generates monthly spending summaries for all users and sends them via email.

    Args:
        app (Flask | None): Optional Flask application instance. If not provided,
            the worker will create a new application context internally.

    Returns:
        None: This function does not return a value. It performs side effects:
            - Iterates over all users in the database.
            - Generates a monthly summary for each user using `get_monthly_summary`.
            - Sends the summary via email using `send_monthly_summary_email`.
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        month = get_previous_month()
        users = UserModel.query.all()

        for user in users:
            try:
                summary = get_monthly_summary(user.id, month)
                send_monthly_summary_email(user_email=user.email, summary=summary)
            except Exception as e:
                print(f"Failed to send summary report for user {user.id}: {e}")