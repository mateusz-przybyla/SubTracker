from rq import Queue

from api.infra.redis import get_redis

def get_email_queue():
    return Queue("emails", connection=get_redis())

def get_reminder_queue():
    return Queue("reminders", connection=get_redis())

def get_report_queue():
    return Queue("reports", connection=get_redis())