import asyncio
import datetime
import uuid

import aiohttp
import pytest
import pytest_asyncio
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_MOVIES


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=test_settings.es_host, verify_certs=False,
        )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(data: list[dict]):
        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(
            index=test_settings.es_index,
            **MAPPING_MOVIES,
            )

        updated, errors = await async_bulk(client=es_client, actions=data)

        await es_client.indices.refresh(index=test_settings.es_index)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(session):
    async def inner(url, query_data):
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, status, headers

    return inner


@pytest_asyncio.fixture(scope="session")
async def redis_client(session):
    client = redis.Redis(host='127.0.0.1', port=6379)
    yield client
    await client.close()


@pytest.fixture
def generate_movies():
    def inner(count: int = 60, title: str = "The Star"):
        return [{
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genres': [
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f11',
                    'name': 'Action',
                    },
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f22',
                    'name': 'Sci-Fi',
                    },
                ],
            'title': title,
            'description': 'New World',
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors_names': ['Stan'],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'},
                ],
            'directors': [
                {'id': 'ef00b8ff-3c82-4d31-ad8e-72b69f4e3f00', 'name': 'Stan'},
                ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {
                    'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6',
                    'name': 'Howard',
                    },
                ],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'film_work_type': 'movie',
            } for _ in range(count)]

    return inner


@pytest.fixture
def make_bulk(generate_movies):
    def inner(docs, index='movies'):
        bulk = []
        for row in docs:
            data = {'_index': index, '_id': row['id']}
            data.update({'_source': row})
            bulk.append(data)
        return bulk

    return inner


@pytest_asyncio.fixture(autouse=True)
async def clear_redis(redis_client):
    await redis_client.flushall()
