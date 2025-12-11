from flask import Flask, current_app

from api.services.reminder_log import create_reminder_log
from api.services.subscription import get_subscriptions_due_in
from api.tasks.email_tasks import send_email_reminder

def check_upcoming_payments(app: Flask | None = None) -> None:
    """
    Check upcoming subscription payments and send reminder emails.

    This task performs the following steps:
    - Loads the Flask application context (if not provided).
    - Queries subscriptions with upcoming payments due in specific day offsets (e.g., 1 and 7 days).
    - Sends reminder emails using `send_email_reminder`.
    - Records success or failure in reminder logs.

    Args:
        app (Flask | None): Optional Flask application instance. If omitted,
            a new Flask app will be created using `create_app()`.

    Returns:
        None
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        subs = get_subscriptions_due_in([1, 7])
        
        if not subs:
            current_app.logger.info("No upcoming payments found.")
            return

        for sub in subs:
            try:
                send_email_reminder(
                    user_email=sub.user.email,
                    subscription_name=sub.name,
                    next_payment_date=sub.next_payment_date,
                )
                create_reminder_log(
                    data={"message": f"Reminder sent for {sub.name}", "success": True},
                    sub_id=sub.id,
                )
                current_app.logger.info(f"Reminder sent | sub_id={sub.id} user={sub.user.email} next_payment={sub.next_payment_date}")
            except Exception as e:               
                create_reminder_log(
                    data={"message": str(e), "success": False}, 
                    sub_id=sub.id,
                )
                current_app.logger.error(f"Failed to send reminder | sub_id={sub.id} error={e}")