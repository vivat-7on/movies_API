import uuid

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_PERSONS

PERSON_ID = str(uuid.uuid4())


@pytest.mark.asyncio
async def test_person_detail_success(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    es_data = generate_persons(
        count=1,
        person_id=PERSON_ID,
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
    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")


@pytest.mark.asyncio
async def test_person_detail_not_found(
    make_get_request,
    ):
    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_person_detail_invalid_uuid(
    make_get_request,
    ):
    invalid_person_uuid = "invalid_uuid"
    url = test_settings.service_url + '/api/v1/persons/{}'.format(
        invalid_person_uuid,
        )

    body, status, _ = await make_get_request(url, {})
    assert status == 422


@pytest.mark.asyncio
async def test_person_detail_cache_works(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(
        count=1,
        person_id=PERSON_ID,
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
    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")


@pytest.mark.asyncio
async def test_person_detail_cache_cleared_and_es_down(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    redis_flush,
    ):
    es_data = generate_persons(
        count=1,
        person_id=PERSON_ID,
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
    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данных нет
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_person_detail_cache_isolation(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    person_id2 = str(uuid.uuid4())
    es_data = generate_persons(
        count=1,
        person_id=PERSON_ID,
        name_prefix="Test Actor",
        )
    es_data.extend(
        generate_persons(
            count=1,
            person_id=person_id2,
            name_prefix="Second Test Actor",
            ),
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
    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")

    # убиваем ES
    await es_client.indices.delete(index="persons")

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == PERSON_ID
    assert body["name"].startswith("Test Actor")

    # Данных нет
    url = test_settings.service_url + '/api/v1/persons/{}'.format(person_id2)
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_person_detail_es_down_initially(
    generate_persons,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_persons(
        count=1,
        person_id=PERSON_ID,
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

    url = test_settings.service_url + '/api/v1/persons/{}'.format(PERSON_ID)
    query = {}
    body, status, _ = await make_get_request(url, query)
    assert status == 404
