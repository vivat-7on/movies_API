import uuid

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_MOVIES, MAPPING_PERSONS


@pytest.mark.parametrize("role", ["actor", "director", "writer"])
@pytest.mark.asyncio
async def test_persons_film_success(
    es_write_data,
    generate_movies_with_person,
    make_bulk,
    generate_persons,
    make_get_request,
    role,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=5,
        role=role,
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 5
    assert len(body["results"]) == 5

    film = body["results"][0]
    assert "uuid" in film
    assert "title" in film
    assert "imdb_rating" in film


@pytest.mark.asyncio
async def test_persons_film_empty(
    es_write_data,
    make_bulk,
    generate_persons,
    make_get_request,
):
    person_id = str(uuid.uuid4())

    # есть person, но нет фильмов
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )
    persons_bulk = make_bulk(docs=persons, index="persons")
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})

    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_film_invalid_uuid(make_get_request):
    person_id = "invalid_uuid"
    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})

    assert status == 422


@pytest.mark.asyncio
async def test_persons_film_person_not_found(
    make_get_request,
):
    person_id = "55fc8aef-bed3-4801-863c-14f1917e9851"
    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 404


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "page_number": 1,
                "page_size": 5,
            },
            {
                "status": 200,
                "page_number": 1,
                "page_size": 5,
                "length": 5,
            },
        ),
        (
            {
                "page_number": 2,
                "page_size": 5,
            },
            {
                "status": 200,
                "page_number": 2,
                "page_size": 5,
                "length": 5,
            },
        ),
        (
            {
                "page_number": 3,
                "page_size": 5,
            },
            {
                "status": 200,
                "page_number": 3,
                "page_size": 5,
                "length": 0,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons_film_pagination(
    es_write_data,
    generate_movies_with_person,
    make_bulk,
    generate_persons,
    make_get_request,
    query_data,
    expected_answer,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=10,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
    }

    body, status, _ = await make_get_request(url, query)
    assert status == expected_answer.get("status")
    assert body["page_number"] == expected_answer.get("page_number")
    assert body["page_size"] == expected_answer.get("page_size")
    assert len(body["results"]) == expected_answer.get("length")
    assert body["count"] == 10


@pytest.mark.asyncio
async def test_persons_film_default_pagination(
    es_write_data,
    generate_movies_with_person,
    make_bulk,
    generate_persons,
    make_get_request,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=60,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["page_number"] == 1
    assert body["page_size"] == 50
    assert body["count"] == 60


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "page_number": 0,
                "page_size": 5,
            },
            {
                "status": 422,
            },
        ),
        (
            {
                "page_number": -1,
                "page_size": 5,
            },
            {
                "status": 422,
            },
        ),
        (
            {
                "page_number": 1,
                "page_size": 0,
            },
            {
                "status": 422,
            },
        ),
        (
            {
                "page_number": 1,
                "page_size": 999,
            },
            {
                "status": 422,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons_film_invalid_pagination(
    es_write_data,
    generate_movies_with_person,
    make_bulk,
    generate_persons,
    make_get_request,
    query_data,
    expected_answer,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=60,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
    }

    body, status, _ = await make_get_request(url, query)
    assert status == expected_answer.get("status")


@pytest.mark.asyncio
async def test_persons_film_cache_works(
    generate_movies_with_person,
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=5,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 5
    assert len(body["results"]) == 5

    film = body["results"][0]
    assert "uuid" in film
    assert "title" in film
    assert "imdb_rating" in film

    # убиваем ES
    await es_client.indices.delete(index="persons")
    await es_client.indices.delete(index="movies")

    # Данные из кеша
    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 5
    assert len(body["results"]) == 5


@pytest.mark.asyncio
async def test_persons_film_cache_cleared(
    generate_movies_with_person,
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    redis_flush,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=5,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 5
    assert len(body["results"]) == 5

    film = body["results"][0]
    assert "uuid" in film
    assert "title" in film
    assert "imdb_rating" in film

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="movies")

    # Данных нет
    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_film_cache_isolation_by_pagination(
    generate_movies_with_person,
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
):
    person_id = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=20,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"
    query = {
        "page_number": 1,
        "page_size": 10,
    }

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    film = body["results"][0]
    assert "uuid" in film
    assert "title" in film
    assert "imdb_rating" in film

    # убиваем ES
    await es_client.indices.delete(index="persons")
    await es_client.indices.delete(index="movies")

    query = {
        "page_number": 2,
        "page_size": 10,
    }

    body, status, _ = await make_get_request(url, query)

    # Таких данных нет
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_film_cache_isolation_by_person(
    generate_movies_with_person,
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
):
    person_id = str(uuid.uuid4())
    person_id2 = str(uuid.uuid4())

    # Создаём person
    persons = generate_persons(
        count=1,
        person_id=person_id,
        name_prefix="Test Person",
    )

    persons.extend(
        generate_persons(
            count=1,
            person_id=person_id2,
            name_prefix="Second Test Person",
        ),
    )

    # Создаём фильмы с этим person
    movies = generate_movies_with_person(
        person_id=person_id,
        count=5,
        role="actor",
    )

    persons_bulk = make_bulk(docs=persons, index="persons")
    movies_bulk = make_bulk(docs=movies, index="movies")

    # Пишем в ES person и movies
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=persons_bulk,
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=movies_bulk,
    )

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"

    body, status, _ = await make_get_request(url, {})
    assert status == 200
    assert body["count"] == 5
    assert len(body["results"]) == 5

    film = body["results"][0]
    assert "uuid" in film
    assert "title" in film
    assert "imdb_rating" in film

    # убиваем ES
    await es_client.indices.delete(index="persons")
    await es_client.indices.delete(index="movies")

    url = test_settings.service_url + f"/api/v1/persons/{person_id2}/film"
    body, status, _ = await make_get_request(url, {})

    # Таких данных нет
    assert status == 404
