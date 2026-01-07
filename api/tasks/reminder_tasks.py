from flask import Flask, current_app
from rq import Retry
from redis import RedisError

from api.services import reminder_log as reminder_log_service
from api.services import subscription as subscription_service
from api.tasks import email_tasks
from api.infra.queues import get_reminder_queue
from api.exceptions import (
    SubscriptionNotFoundError, 
    ReminderLogCreateError, 
    EmailTemporaryError, 
    EmailPermanentError
)

def check_upcoming_payments(app: Flask | None = None) -> None:
    """
    Enqueue reminder jobs for subscriptions with upcoming payments.

    This task retrieves subscriptions with payments due soon (e.g. in 1 or 7 days)
    and enqueues a separate background job per subscription to handle email
    sending and logging. The task itself does not send emails directly.

    Args:
        app (Flask | None): Optional Flask application instance. If not provided,
            the application will be created via `create_app()`.

    Returns:
        None
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        subs = subscription_service.get_subscriptions_due_in([1, 7])

        if not subs:
            current_app.logger.info("No upcoming payments found")
            return

        for sub in subs:
            try:
                get_reminder_queue().enqueue(
                    send_single_subscription_reminder,
                    sub.id,
                    retry=Retry(max=3, interval=[30, 60, 120]),
                    job_timeout=60
                )
            except RedisError as e:
                current_app.logger.error(
                    "Failed to enqueue reminder task",
                    extra={"error": str(e), "sub_id": sub.id}
                )

def send_single_subscription_reminder(sub_id: int, app: Flask | None = None) -> None:
    """
    Send a reminder email for a single subscription.

    This task fetches the subscription, sends a reminder email to the owner
    and persists a reminder log indicating success or failure.

    Args:
        sub_id (int): Identifier of the subscription.
        app (Flask | None): Optional Flask application instance. If not provided,
            the application will be created via `create_app()`.

    Returns:
        None
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        try:
            sub = subscription_service.get_subscription_by_id(sub_id)
        except SubscriptionNotFoundError:
            current_app.logger.warning(
                "Subscription not found for reminder task",
                extra={"sub_id": sub_id},
            )
            return
        try:
            email_tasks.send_email_reminder(
                user_email=sub.user.email,
                subscription_name=sub.name,
                next_payment_date=sub.next_payment_date,
            )
        except EmailTemporaryError:
            raise 
        except EmailPermanentError as e:
            try:
                reminder_log_service.create_reminder_log(
                    data={"message": str(e), "success": False},
                    sub_id=sub.id,
                )
            except ReminderLogCreateError as log_err:
                current_app.logger.error(
                    "Failed to log failed reminder",
                    extra={"sub_id": sub.id, "error": str(log_err)},
                )
            return
        try:
            reminder_log_service.create_reminder_log(
                data={"message": f"Reminder sent for {sub.name}", "success": True},
                sub_id=sub.id,
            )
        except ReminderLogCreateError as log_err:
            current_app.logger.error(
                "Failed to log successful reminder",
                extra={"error": str(log_err), "sub_id": sub.id},
            )