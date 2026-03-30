import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_GENRES

GENRE_ID = "383fa609-62cd-4150-a5d4-6ec9c1a76d18"


@pytest.mark.asyncio
async def test_genre_detail_success(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )
    url = test_settings.service_url + '/api/v1/genres/{}'.format(GENRE_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == GENRE_ID
    assert body["name"] == "Action 0"


@pytest.mark.asyncio
async def test_genre_detail_not_found(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    ):
    search_genre_id = "b8c98290-bb2e-4563-aae6-6feff49f7d70"
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )
    url = test_settings.service_url + '/api/v1/genres/{}'.format(
        search_genre_id,
        )
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_genre_detail_invalid_uuid(
    make_get_request,
    ):
    invalid_genre_id = "invalid-uuid"
    url = test_settings.service_url + '/api/v1/genres/{}'.format(
        invalid_genre_id,
        )
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 422


@pytest.mark.asyncio
async def test_genre_detail_cache_works(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )
    url = test_settings.service_url + '/api/v1/genres/{}'.format(GENRE_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == GENRE_ID
    assert body["name"] == "Action 0"

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == GENRE_ID
    assert body["name"] == "Action 0"


@pytest.mark.asyncio
async def test_genre_detail_cache_cleared_and_es_down(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    redis_flush,
    ):
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )
    url = test_settings.service_url + '/api/v1/genres/{}'.format(GENRE_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == GENRE_ID
    assert body["name"] == "Action 0"

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_genre_detail_cache_isolation(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    search_genre_id = "b8c98290-bb2e-4563-aae6-6feff49f7d70"
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )
    url = test_settings.service_url + '/api/v1/genres/{}'.format(GENRE_ID)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert set(body.keys()) == {"uuid", "name"}
    assert body["uuid"] == GENRE_ID
    assert body["name"] == "Action 0"

    # убиваем ES
    await es_client.indices.delete(index="genres")

    # Таких данных в кеше быть не должно
    url = test_settings.service_url + '/api/v1/genres/{}'.format(
        search_genre_id,
        )
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_genre_detail_es_down_initially(
    generate_genres,
    make_bulk,
    es_write_data,
    make_get_request,
    es_client,
    ):
    es_data = generate_genres(
        count=1,
        genre_id=GENRE_ID,
        name_prefix="Action",
        )
    bulk = make_bulk(
        docs=es_data,
        index="genres",
        )
    await es_write_data(
        index="genres",
        mapping=MAPPING_GENRES,
        data=bulk,
        )

    # убили ES ДО первого запроса
    await es_client.indices.delete(index="genres")

    url = test_settings.service_url + f'/api/v1/genres/{GENRE_ID}'
    body, status, _ = await make_get_request(url, {})

    assert status == 404
