from redis.asyncio import Redis

_client: Redis | None = None


def set_redis_client(redis: Redis):
    global _client
    _client = redis


def get_redis() -> Redis:
    if _client is None:
        raise RuntimeError("redis client not set")
    return _client


def reset_redis_client():
    global _client
    _client = None
