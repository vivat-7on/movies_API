import pytest_asyncio
import redis.asyncio as redis

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = redis.Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port,
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def clear_redis(redis_client):
    await redis_client.flushall()


@pytest_asyncio.fixture
def redis_flush(redis_client):
    async def inner():
        await redis_client.flushall()

    return inner
