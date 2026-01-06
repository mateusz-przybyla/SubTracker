from datetime import datetime, timezone, timedelta
from rq_scheduler import Scheduler

from api.tasks import reminder_tasks, report_tasks
from api.infra.redis import get_redis
from api.infra.queues import get_reminder_queue, get_report_queue

scheduler = Scheduler(connection=get_redis())

def register_reminder_job() -> None:
    """Register the daily reminder job for upcoming subscription payments."""
    existing_job = [job for job in scheduler.get_jobs() if job.id == "subscription_payment_reminder_job"]
    if existing_job:
        print("Reminder job already scheduled.")
        return

    scheduler.schedule(
        scheduled_time=datetime.now(timezone.utc) + timedelta(seconds=10),
        func=reminder_tasks.check_upcoming_payments,
        interval=86400, # 24h in seconds
        repeat=None,
        id="subscription_payment_reminder_job",
        queue_name=get_reminder_queue().name
    )
    print("Reminder job scheduled.")

def register_report_job() -> None:
    """
    Register the monthly report job for spending summaries.
    """
    if scheduler.connection.exists("rq:scheduler:job:monthly_report_job"):
        print("Monthly report job already scheduled.")
        return

    scheduler.cron(
        cron_string="0 0 1 * *",
        func=report_tasks.generate_monthly_report,
        id="monthly_report_job",
        queue_name=get_report_queue().name,
        use_local_timezone=True
    )
    print("Monthly report job scheduled.")

def register_jobs() -> None:
    print("Registering scheduled jobs...")
    register_reminder_job()
    register_report_job()

def debug_list_jobs() -> None:
    """
    Print all jobs currently registered in the scheduler for debugging purposes.
    """
    jobs = list(scheduler.get_jobs())

    print(f"Found {len(jobs)} job(s):")
    for job in jobs:
        print(f"- ID: {job.id}")
        print(f"  Func: {job.func_name}")
        print(f"  Queue: {job.origin}")
        if "registered_at" in job.meta:
            print(f"  Registered at: {job.meta['registered_at']}")
        print()

if __name__ == "__main__":
    register_jobs()