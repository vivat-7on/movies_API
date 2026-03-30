import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_PERSONS

BASE_URL = test_settings.service_url + '/api/v1/persons/search'


@pytest.mark.asyncio
async def test_persons_search_by_query(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "James"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    query = {"query": "Potato"}
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {
                    "page_number": 1,
                    "page_size": 20,
                    },
                {
                    "status": 200,
                    "length": 20,
                    },
            ),
        (
                {
                    "page_number": 2,
                    "page_size": 20,
                    },
                {
                    "status": 200,
                    "length": 20,
                    },
            ),
        (
                {
                    "page_number": 99,
                    "page_size": 20,
                    },
                {
                    "status": 200,
                    "length": 0,
                    },
            ),
        ],
    )
@pytest.mark.asyncio
async def test_persons_search_pagination(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    query_data,
    expected_answer,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {
        "query": "James",
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")
    assert body["count"] == 60
    assert len(body["results"]) == expected_answer.get("length")


@pytest.mark.asyncio
async def test_persons_search_default_pagination(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "James"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["page_number"] == 1
    assert body["page_size"] == 50
    assert body["count"] == 60
    assert len(body["results"]) == 50


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {
                    "query": "",
                    "page_number": 1,
                    "page_size": 10,
                    },
                {
                    "status": 422,
                    },
            ),
        (
                {
                    "query": "James",
                    "page_number": 0,
                    "page_size": 10,
                    },
                {
                    "status": 422,
                    },
            ),
        (
                {
                    "query": "James",
                    "page_number": -1,
                    "page_size": 10,
                    },
                {
                    "status": 422,
                    },
            ),
        (
                {
                    "query": "James",
                    "page_number": 1,
                    "page_size": 0,
                    },
                {
                    "status": 422,
                    },
            ),
        (
                {
                    "query": "James",
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
async def test_persons_search_invalid_params(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    query_data,
    expected_answer,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {
        "query": query_data.get("query"),
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")


@pytest.mark.asyncio
async def test_persons_search_whitespace_query(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "  "}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_search_cache_works(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    es_client,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "James"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50


@pytest.mark.asyncio
async def test_persons_search_cache_cleared(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    es_client,
    redis_flush,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "James"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данных нет
    body, status, _ = await make_get_request(BASE_URL, query)
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_search_cache_isolation(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    es_client,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {"query": "James"}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    query = {"query": "Alice"}

    # Таких данных нет
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_search_cache_isolation_by_pagination(
    es_write_data,
    make_get_request,
    generate_persons,
    make_bulk,
    es_client,
    ):
    es_data = generate_persons(count=60, name_prefix="James Carrey")
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)
    query = {
        "query": "James",
        "page_number": 1,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    query = {
        "query": "James",
        "page_number": 2,
        }

    # Таких данных нет
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_search_es_down_initially(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(count=20)
    bulk = make_bulk(docs=es_data, index="persons")
    await es_write_data(index="persons", mapping=MAPPING_PERSONS, data=bulk)

    # убили ES ДО первого запроса
    await es_client.indices.delete(index="persons")

    query = {"query": "James"}
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []
