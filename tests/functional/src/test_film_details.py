import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_MOVIES


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "film_id": "c6f9460c-ed85-4076-9f52-19b5c67b4178",
                "search_film_id": "c6f9460c-ed85-4076-9f52-19b5c67b4178",
            },
            {
                "status_code": 200,
                "request_film_id": "c6f9460c-ed85-4076-9f52-19b5c67b4178",
            },
        ),
        (
            {
                "film_id": "c6f9460c-ed85-4076-9f52-19b5c67b4178",
                "search_film_id": "11111111-1111-1111-1111-111111111111",
            },
            {
                "status_code": 404,
                "request_film_id": "",
            },
        ),
        (
            {
                "film_id": "c6f9460c-ed85-4076-9f52-19b5c67b4178",
                "search_film_id": "invalid_uuid",
            },
            {
                "status_code": 422,
                "request_film_id": "",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_detail_by_id(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
):
    title = "The Star"
    film_id = query_data.get("film_id")
    search_film_id = query_data.get("search_film_id")

    es_data = generate_movies(1, title, film_id)
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    url = test_settings.service_url + "/api/v1/films/{}".format(search_film_id)
    query = {}
    body, status, _ = await make_get_request(url, query)
    assert status == expected_answer.get("status_code")
    if status == 200:
        assert body["uuid"] == expected_answer.get("request_film_id")
        assert body["title"] == title


@pytest.mark.asyncio
async def test_film_detail_cache_works(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
):
    title = "The Star"
    film_id = "c6f9460c-ed85-4076-9f52-19b5c67b4178"
    es_data = generate_movies(1, title, film_id)
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )
    url = test_settings.service_url + "/api/v1/films/{}".format(film_id)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["uuid"] == film_id
    assert body["title"] == title

    # убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["uuid"] == film_id
    assert body["title"] == title


@pytest.mark.asyncio
async def test_film_detail_cache_isolation(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
):
    title = "The Star"
    film_first_id = "c6f9460c-ed85-4076-9f52-19b5c67b4178"
    film_second_id = "7c73d579-f394-4153-aa41-eee981f36f13"
    es_data = generate_movies(1, title, film_first_id)
    es_data.extend(generate_movies(1, title, film_second_id))
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    url = test_settings.service_url + "/api/v1/films/{}".format(film_first_id)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["uuid"] == film_first_id
    assert body["title"] == title

    # убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # Данные из кеша
    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["uuid"] == film_first_id
    assert body["title"] == title

    # Таких данных в кеше быть не должно
    url = test_settings.service_url + "/api/v1/films/{}".format(film_second_id)
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_film_detail_cache_expired_or_cleared(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    redis_flush,
):
    title = "The Star"
    film_id = "c6f9460c-ed85-4076-9f52-19b5c67b4178"
    es_data = generate_movies(1, title, film_id)
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )
    url = test_settings.service_url + "/api/v1/films/{}".format(film_id)
    query = {}

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert body["uuid"] == film_id
    assert body["title"] == title

    # Сбрасываем кэш
    await redis_flush()

    # убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # Данных нет
    body, status, _ = await make_get_request(url, query)
    assert status == 404


@pytest.mark.asyncio
async def test_film_detail_es_down_initially(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
):
    title = "The Star"
    film_id = "c6f9460c-ed85-4076-9f52-19b5c67b4178"
    es_data = generate_movies(1, title, film_id)
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    # ES умер до первого запроса
    await es_client.indices.delete(index=test_settings.es_index)

    url = test_settings.service_url + "/api/v1/films/{}".format(film_id)
    query = {}

    # Данных нет
    body, status, _ = await make_get_request(url, query)
    assert status == 404
