import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_GENRES

BASE_URL = test_settings.service_url + "/api/v1/genres"


@pytest.mark.asyncio
async def test_genres_list_basic(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": 1,
        "page_size": 10,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {
                    "page_number": 1,
                    "page_size": 10,
                    },
                {
                    "status": 200,
                    "length": 10,
                    },
            ),
        (
                {
                    "page_number": 2,
                    "page_size": 10,
                    },
                {
                    "status": 200,
                    "length": 10,
                    },
            ),
        (
                {
                    "page_number": 999,
                    "page_size": 10,
                    },
                {
                    "status": 200,
                    "length": 0,
                    },
            ),
        ],
    )
@pytest.mark.asyncio
async def test_genres_list_pagination(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")
    assert body["count"] == 20
    assert len(body["results"]) == expected_answer.get("length")


@pytest.mark.asyncio
async def test_genres_list_default_pagination(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    ):
    es_data = generate_genres(count=60)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert body["page_number"] == 1
    assert body["page_size"] == 50
    assert len(body["results"]) == 50


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
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
        (
                {
                    "page_number": 0,
                    "page_size": 10,
                    },
                {
                    "status": 422,
                    },
            ),
        (
                {
                    "page_number": -1,
                    "page_size": 10,
                    },
                {
                    "status": 422,
                    },
            ),
        ],
    )
@pytest.mark.asyncio
async def test_genres_list_invalid_params(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")



@pytest.mark.asyncio
async def test_genres_list_search(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    ):
    es_data = []
    es_data.extend(generate_genres(1, name_prefix="Action"))
    es_data.extend(generate_genres(1, name_prefix="Drama"))
    es_data.extend(generate_genres(1, name_prefix="Comedy"))
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {"search": "Action"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 1
    assert body["results"][0]["name"].startswith("Action")

    query = {"search": "Drama"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 1
    assert body["results"][0]["name"].startswith("Drama")

    query = {"search": "Comedy"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 1
    assert body["results"][0]["name"].startswith("Comedy")

    query = {"search": "XXX"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0


@pytest.mark.parametrize(
    "query_data, reverse",
    [
        ({"sort": "name"}, False),
        ({"sort": "-name"}, True),
    ],
)
@pytest.mark.asyncio
async def test_genres_list_sort(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    query_data,
    reverse,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "sort": query_data.get("sort"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    names = [g["name"] for g in body["results"]]
    assert names == sorted(names, reverse=reverse)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {
                    "sort": "-name",
                    "page_number": 1,
                    "page_size": 10,
                    },
                {"reverse": 1},
            ),
        (
                {
                    "sort": "name",
                    "page_number": 2,
                    "page_size": 10,
                    },
                {"reverse": 0},
            ),
        ],
    )
@pytest.mark.asyncio
async def test_genres_list_sort_with_pagination(
    es_write_data,
    generate_genres,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "sort": query_data.get("sort"),
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    names = [g["name"] for g in body["results"]]
    assert len(names) == body["page_size"]
    assert names == sorted(names, reverse=bool(expected_answer.get("reverse")))


@pytest.mark.asyncio
async def test_genres_list_cache_works(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": 1,
        "page_size": 10,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10


@pytest.mark.asyncio
async def test_genres_list_cache_cleared(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    redis_flush,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": 1,
        "page_size": 10,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Данных нет
    body, status, _ = await make_get_request(BASE_URL, query)
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_genres_list_cache_isolation(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)
    query = {
        "page_number": 1,
        "page_size": 10,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    # Таких данных в кеше нет
    query = {
        "page_number": 2,
        "page_size": 10,
        }
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_genres_list_es_down_initially(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_genres(count=20)
    bulk = make_bulk(docs=es_data, index="genres")
    await es_write_data(index="genres", mapping=MAPPING_GENRES, data=bulk)

    # убили ES ДО первого запроса
    await es_client.indices.delete(index="genres")

    body, status, _ = await make_get_request(BASE_URL, {})

    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []
