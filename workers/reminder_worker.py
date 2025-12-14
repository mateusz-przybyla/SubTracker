from rq import Worker

from api.infra.queues import get_reminder_queue

if __name__ == "__main__":
    worker = Worker([get_reminder_queue()])
    worker.work()