from flask import current_app
from rq import Retry
from redis import RedisError
from datetime import datetime, timezone

from api.services import subscription as subscription_service
from api.services import user as user_service
from api.utils import date_helpers
from api.tasks import email_tasks
from api.infra.queues import get_report_queue
from api.exceptions import (
    EmailPermanentError, 
    EmailTemporaryError, 
    UserNotFoundError
)

def generate_monthly_report() -> None:
    """
    Enqueue monthly summary report jobs for all users.

    This task is responsible only for orchestration:
    - Loads Flask application context.
    - Determines the target month.
    - Fetches all users.
    - Enqueues a separate background job per user.

    Each user report is processed independently to ensure
    fault isolation and retry capability.
    """
    month = date_helpers.get_previous_month(datetime.now(timezone.utc))
    users = user_service.get_all_users()

    for user in users:
        try:
            get_report_queue().enqueue(
                send_single_user_monthly_report,
                user.id,
                month,
                retry=Retry(max=3, interval=[30, 60, 120]),
                job_timeout=60
            )
        except RedisError as e:
            current_app.logger.error(
                "Failed to enqueue report task",
                extra={"error": str(e), "user_id": user.id}
            )

def send_single_user_monthly_report(user_id: int, month: str) -> None:
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
    """
    summary = subscription_service.get_monthly_summary(
        user_id=user_id,
        month=month
    )
    if not summary or summary.get("total_spent", 0) == 0:
        return

    try:
        user = user_service.get_user_by_id(user_id)
    except UserNotFoundError:
        current_app.logger.warning(
            "User not found for monthly report",
            extra={"user_id": user_id, "month": month}
        )
        return

    try:
        email_tasks.send_monthly_summary_email(
            user_email=user.email,
            summary=summary
        )
    except EmailTemporaryError:
        raise
    except EmailPermanentError as e:
        current_app.logger.error(
            "Failed to send monthly summary report",
            extra={
                "user_id": user_id,
                "month": month,
                "error": str(e)
            }
        )