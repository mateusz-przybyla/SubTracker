from rq import Worker

from api.infra.queues import get_email_queue

if __name__ == "__main__":
    worker = Worker([get_email_queue()])
    worker.work()