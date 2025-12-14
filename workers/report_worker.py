from rq import Worker

from api.infra.queues import get_report_queue

if __name__ == "__main__":
    worker = Worker([get_report_queue()])
    worker.work()