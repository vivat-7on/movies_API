import asyncio
import datetime
import uuid

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    hosts = f"http://{test_settings.es_host}:{test_settings.es_port}"
    es_client = AsyncElasticsearch(
        hosts=hosts, verify_certs=False,
        )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(session):
    async def inner(url, query_data):
        async with session.get(url, params=query_data) as response:
            text = await response.text()
            try:
                body = await response.json()
            except Exception:
                body = await response.text()
            headers = response.headers
            status = response.status
        return body, status, headers

    return inner


@pytest.fixture
def generate_movies():
    def inner(
        count: int = 60,
        title: str = "The Star",
        film_id: str | None = None,
        rating: float = 8.5,
        genres: list[dict] | None = None,
        ) -> list[dict]:
        if genres is None:
            genres = [
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f11',
                    'name': 'Action',
                    },
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f22',
                    'name': 'Sci-Fi',
                    },
                ]
        return [{
            'id': film_id if film_id is not None else str(uuid.uuid4()),
            'imdb_rating': rating,
            'genres': genres,
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
    def inner(docs, index):
        bulk = []
        for row in docs:
            data = {'_index': index, '_id': row['id']}
            data.update({'_source': row})
            bulk.append(data)
        return bulk

    return inner


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(index: str, mapping: dict, data: list[dict]):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        await es_client.indices.create(
            index=index,
            **mapping,
            )

        updated, errors = await async_bulk(client=es_client, actions=data)
        await es_client.indices.refresh(index=index)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def generate_genres():
    def inner(
        count: int = 10,
        genre_id: str | None = None,
        name_prefix: str | None = "Genre",
        ) -> list[dict]:
        genres = []

        for i in range(count):
            genres.append(
                {
                    "id": genre_id if genre_id else str(uuid.uuid4()),
                    "name": f"{name_prefix} {i}",
                    },
                )

        return genres

    return inner


@pytest.fixture
def generate_persons():
    def inner(
        count: int = 10,
        person_id: str | None = None,
        name_prefix: str | None = "Person",
        ) -> list[dict]:
        genres = []

        for i in range(count):
            genres.append(
                {
                    "id": person_id if person_id else str(uuid.uuid4()),
                    "name": f"{name_prefix} {i}",
                    },
                )

        return genres

    return inner


@pytest.fixture
def generate_movies_with_person():
    def inner(
        person_id: str,
        count: int = 60,
        role: str = "actor",  # actor | director | writer
        ) -> list[dict]:

        def build_role(role_name: str) -> list[dict]:
            if role == role_name:
                return [{"id": person_id, "name": "Test Person"}]
            return []

        return [{
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genres': [
                {'id': str(uuid.uuid4()), 'name': 'Action'},
                ],
            'title': f"Film {i}",
            'description': 'New World',
            'actors_names': ['Test Person'] if role == 'actors' else [],
            'writers_names': ['Test Person'] if role == 'directors' else [],
            'directors_names': ['Test Person'] if role == 'writers' else [],
            'actors': build_role('actor'),
            'directors': build_role('director'),
            'writers': build_role('writer'),
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'film_work_type': 'movie',
            } for i in range(count)]

    return inner


@pytest_asyncio.fixture(autouse=True)
async def clear_es(es_client):
    await es_client.indices.delete(index="persons", ignore_unavailable=True)
    await es_client.indices.delete(index="movies", ignore_unavailable=True)
    await es_client.indices.delete(index="genres", ignore_unavailable=True)
