import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_PERSONS

BASE_URL = test_settings.service_url + "/api/v1/persons"


@pytest.mark.asyncio
async def test_persons_list_basic(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    es_data = generate_persons(
        count=60,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )

    body, status, _ = await make_get_request(BASE_URL, {})
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50
    person = body["results"][0]
    assert set(person.keys()) == {"uuid", "name"}


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
async def test_persons_list_pagination(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")
    assert body["count"] == 20
    assert len(body["results"]) == expected_answer.get("length")


@pytest.mark.asyncio
async def test_persons_list_default_pagination(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    es_data = generate_persons(
        count=60,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )

    body, status, _ = await make_get_request(BASE_URL, {})
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
async def test_persons_list_invalid_params(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )
    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == expected_answer.get("status")


@pytest.mark.parametrize(
    "query_data, reverse",
    [
        ({"sort": "name"}, False),
        ({"sort": "-name"}, True),
        ],
    )
@pytest.mark.asyncio
async def test_persons_list_sort(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    query_data,
    reverse,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )
    query = {
        "sort": query_data.get("sort"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    names = [p["name"] for p in body["results"]]
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
async def test_persons_list_sort_with_pagination(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    query_data,
    expected_answer,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )
    query = {
        "sort": query_data.get("sort"),
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    names = [p["name"] for p in body["results"]]
    assert names == sorted(names, reverse=bool(expected_answer.get("reverse")))


@pytest.mark.asyncio
async def test_persons_list_cache_works(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(
        count=60,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )

    body, status, _ = await make_get_request(BASE_URL, {})
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(BASE_URL, {})
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50


@pytest.mark.asyncio
async def test_persons_list_cache_cleared(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    redis_flush,
    ):
    es_data = generate_persons(
        count=60,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )

    body, status, _ = await make_get_request(BASE_URL, {})
    assert status == 200
    assert body["count"] == 60
    assert len(body["results"]) == 50

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данных нет
    body, status, _ = await make_get_request(BASE_URL, {})
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_persons_list_cache_isolation(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )
    query = {
        "page_number": 1,
        "page_size": 10,
        }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["count"] == 20
    assert len(body["results"]) == 10

    # убиваем ES
    await es_client.indices.delete(index="persons")

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
async def test_persons_list_es_down_initially(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(
        count=20,
        name_prefix="Test Actor",
        )
    bulk = make_bulk(
        docs=es_data,
        index="persons",
        )
    await es_write_data(
        index="persons",
        mapping=MAPPING_PERSONS,
        data=bulk,
        )

    # убили ES ДО первого запроса
    await es_client.indices.delete(index="persons")

    body, status, _ = await make_get_request(BASE_URL, {})

    assert status == 200
    assert body["count"] == 0
    assert body["results"] == []
