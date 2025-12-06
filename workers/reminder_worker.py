from flask import Flask

from api.services.reminder_log import create_reminder_log
from api.services.subscription import get_subscriptions_due_in
from workers.mail_worker import send_email_reminder

def check_upcoming_payments(app: Flask | None = None) -> None:
    """
    Worker that checks for upcoming subscription payments and sends reminder emails.

    Args:
        app (Flask | None): Optional Flask application instance. If not provided,
            the worker will create a new application context internally.

    Returns:
        None: This function does not return a value. It performs side effects:
            - Queries subscriptions with upcoming payments due in specific day offsets (e.g., 1 and 7 days).
            - Sends reminder emails to users using `send_email_reminder`.
            - Creates reminder logs for each subscription to record success or failure.
    """
    if app is None:
        from api import create_app
        app = create_app()

    with app.app_context():
        subs = get_subscriptions_due_in([1, 7])
        
        if not subs:
            print("No upcoming payments found.")
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
            except Exception as e:
                print(f"Failed to send reminder for {sub.id}: {e}")
                create_reminder_log(
                    data={"message": str(e), "success": False}, 
                    sub_id=sub.id,
                )