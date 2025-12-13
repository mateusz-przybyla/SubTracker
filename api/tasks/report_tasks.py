from flask import Flask, current_app

from api.services import subscription as subscription_service
from api.services import user as user_service
from api.utils import date_helpers
from api.tasks import email_tasks

def generate_monthly_report(app: Flask | None = None) -> None:
    """
    Generates monthly spending summaries for all users and sends them via email.

    This task performs the following steps:
    - Loads the Flask application context (if not provided).
    - Iterates over all users in the database.
    - Generates a monthly summary for each user using `get_monthly_summary`.
    - Sends the summary via email using `send_monthly_summary_email`.
    
    Args:
        app (Flask | None): Optional Flask application instance. If not provided,
            the task will create a new application context internally.

    Returns: 
        None
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        month = date_helpers.get_previous_month()
        users = user_service.get_all_users()

        for user in users:
            try:
                summary = subscription_service.get_monthly_summary(user.id, month)

                # Skip users with no spending
                if summary['total_spent'] == 0:
                    continue

                email_tasks.send_monthly_summary_email(user_email=user.email, summary=summary)
            except Exception as e:
                current_app.logger.error("Failed to send summary report", extra={
                    "user_id": user.id,
                    "error": str(e)
                })