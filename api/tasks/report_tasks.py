from flask import Flask, current_app
from rq import Retry

from api.services import subscription as subscription_service
from api.services import user as user_service
from api.utils import date_helpers
from api.tasks import email_tasks
from api.infra.queues import get_report_queue

def generate_monthly_report(app: Flask | None = None) -> None:
    """
    Enqueue monthly summary report jobs for all users.

    This task is responsible only for orchestration:
    - Loads Flask application context.
    - Determines the target month.
    - Fetches all users.
    - Enqueues a separate background job per user.

    Each user report is processed independently to ensure
    fault isolation and retry capability.

    Args:
        app (Flask | None): Optional Flask application instance.
            If not provided, a new app will be created internally.
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        month = date_helpers.get_previous_month()
        users = user_service.get_all_users()

        for user in users:
            get_report_queue().enqueue(
            send_single_user_monthly_report,
            user.id,
            month,
            retry=Retry(max=3, interval=60)
        )

def send_single_user_monthly_report(user_id: int, month: str, app: Flask | None = None):
    """
    Generate and send a monthly subscription summary for a single user.

    This task:
    - Loads Flask application context.
    - Calculates user's monthly spending summary.
    - Skips users with zero spending.
    - Sends summary email.
    - Logs failures without crashing the worker.

    Args:
        user_id (int): ID of the user.
        month (str): Month in YYYY-MM format.
        app (Flask | None): Optional Flask application instance.
            If not provided, a new app will be created internally.
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        summary = subscription_service.get_monthly_summary(
            user_id=user_id,
            month=month
        )
        if summary['total_spent'] == 0:
            return

        user = user_service.get_user_by_id(user_id)

        try:
            email_tasks.send_monthly_summary_email(
                user_email=user.email,
                summary=summary
            )
        except Exception as e:
            current_app.logger.error(
                "Failed to send monthly summary report",
                extra={
                    "user_id": user_id,
                    "month": month,
                    "error": str(e)
                }
            )