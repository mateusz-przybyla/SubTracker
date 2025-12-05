from datetime import datetime, timezone, timedelta
from rq_scheduler import Scheduler

from api.extensions import redis_client, reminder_queue, report_queue
from workers.reminder_worker import check_upcoming_payments
from workers.report_worker import generate_monthly_report

reminder_scheduler = Scheduler(queue=reminder_queue, connection=redis_client)
report_scheduler = Scheduler(queue=report_queue, connection=redis_client)

def register_reminder_job() -> None:
    """Register the daily reminder job for upcoming subscription payments."""
    if any(job.id == "subscription_payment_reminder_job" for job in reminder_scheduler.get_jobs()):
        print("Reminder job already scheduled.")
        return

    reminder_scheduler.schedule(
        scheduled_time=datetime.now(timezone.utc) + timedelta(seconds=10),
        func=check_upcoming_payments,
        interval=86400, # 24h in seconds
        repeat=None,
        queue_name=reminder_queue.name,
        id="subscription_payment_reminder_job"
    )
    print("Reminder job scheduled.")

def register_report_job() -> None:
    """Register the monthly report job for spending summaries."""
    if any(job.id == "monthly_report_job" for job in report_scheduler.get_jobs()):
        print("Monthly report job already scheduled.")
        return

    now = datetime.now(timezone.utc)
    if now.month == 12:
        first_of_next_month = datetime(year=now.year + 1, month=1, day=1, tzinfo=timezone.utc)
    else:
        first_of_next_month = datetime(year=now.year, month=now.month + 1, day=1, tzinfo=timezone.utc)

    report_scheduler.schedule(
        scheduled_time=first_of_next_month,
        func=generate_monthly_report,
        interval=2592000,  # ~30 days in seconds
        repeat=None,
        queue_name=report_queue.name,
        id="monthly_report_job"
    )
    print("Monthly report job scheduled.")

def register_jobs() -> None:
    """Register all scheduled jobs."""
    print("Registering scheduled jobs...")
    register_reminder_job()
    register_report_job()

def debug_list_jobs(scheduler) -> None:
    """Print jobs currently registered in the scheduler for debugging purposes."""
    jobs = list(scheduler.get_jobs())

    print(f"Found {len(jobs)} job(s):")
    for job in jobs:
        print(f"- ID: {job.id}")
        print(f"  Func: {job.func_name}")
        print(f"  Queue: {job.origin}")
        if "registered_at" in job.meta:
            print(f"  Registered at: {job.meta['registered_at']}")
        print()