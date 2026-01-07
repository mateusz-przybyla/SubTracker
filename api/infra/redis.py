import os
import redis

_redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def get_redis():
    return _redis