from rq import Worker

from api import create_app
from api.infra.redis import get_redis
from api.infra.queues import get_reminder_queue

if __name__ == "__main__":
    app = create_app()

    redis_conn = get_redis()

    with app.app_context():
        worker = Worker([get_reminder_queue()], connection=redis_conn)
        worker.work()