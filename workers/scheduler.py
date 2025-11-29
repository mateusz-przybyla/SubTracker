from datetime import datetime, timezone, timedelta
from rq_scheduler import Scheduler

from api.extensions import redis_client, reminder_queue
from workers.reminder_worker import check_upcoming_payments

scheduler = Scheduler(
    queue=reminder_queue,
    connection=redis_client
)

def register_jobs() -> None:
    """
    Register the scheduled reminder job for upcoming subscription payments.

    Ensures that the job is only registered once. If already present,
    skips registration. The job runs `check_upcoming_payments` periodically.
    """
    print("Registering scheduled reminder jobs...")

    existing = [job for job in scheduler.get_jobs() if job.id == "subscription_payment_reminder_job"]
    if existing:
        print("Reminder already scheduled.")
        # Development: list all jobs for debugging
        # debug_list_jobs()
        return

    scheduler.schedule(
        scheduled_time=datetime.now(timezone.utc) + timedelta(seconds=10),
        func=check_upcoming_payments,
        interval=86400,  # 24h in seconds
        repeat=None,
        queue_name=reminder_queue.name,
        id="subscription_payment_reminder_job"
    )

    print("Job scheduled.")
    # Development: list all jobs for debugging
    # debug_list_jobs()

def debug_list_jobs() -> None:
    """Print all jobs currently registered in the scheduler for debugging purposes."""
    jobs = list(scheduler.get_jobs())

    print(f"Found {len(jobs)} job(s):")
    for job in jobs:
        print(f"- ID: {job.id}")
        print(f"  Func: {job.func_name}")
        print(f"  Queue: {job.origin}")
        if "registered_at" in job.meta:
            print(f"  Registered at: {job.meta['registered_at']}")
        print()