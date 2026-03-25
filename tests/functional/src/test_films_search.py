import pytest

from tests.functional.fixtures.es import es_client
from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (  # есть результаты
                {"query": "The Star"},
                {
                    "status": 200,
                    "length": 50,
                    "count": 60,
                    },
            ),
        (  # нет результатов
                {"query": "Mashed potato"},
                {
                    "status": 200,
                    "length": 0,
                    "count": 0,
                    },
            ),
        ],
    )
@pytest.mark.asyncio
async def test_films_search_by_query(
    query_data,
    expected_answer,
    es_write_data,
    make_get_request,
    generate_movies,
    make_bulk,
    ):
    # 1. Генерируем данные для ES
    es_data = generate_movies(60, "The Star")
    bulk_query = make_bulk(es_data)

    # 2. Загружаем данные в ES
    await es_write_data(bulk_query)

    # 3. Запрашиваем данные из ES по API
    url = test_settings.service_url + '/api/v1/films/search'
    body, status, _ = await make_get_request(url, query_data)

    # 4. Проверяем ответ
    assert status == expected_answer.get('status')
    assert len(body["results"]) == expected_answer.get('length')
    assert body["count"] == expected_answer.get('count')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (  # первая страница
                {
                    "page_size": 20,
                    "page_number": 1,
                    },
                {"length": 20},
            ),
        (  # вторая страница
                {
                    "page_size": 20,
                    "page_number": 2,
                    },
                {"length": 20},
            ),
        (  # страница на которую не хватило данных
                {
                    "page_size": 20,
                    "page_number": 99,
                    },
                {"length": 0},
            ),
        ],
    )
@pytest.mark.asyncio
async def test_films_search_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(60, "The Star")
    bulk = make_bulk(docs)

    # 2. Загружаем данные в ES
    await es_write_data(bulk)

    # 3. Запрашиваем данные из ES по API
    url = test_settings.service_url + '/api/v1/films/search'
    query = {
        "query": "The Star",
        "page_size": query_data.get('page_size'),
        "page_number": query_data.get('page_number'),
        }

    body, status, _ = await make_get_request(url, query)
    assert status == 200
    assert len(body['results']) == expected_answer.get("length")


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "query": "The Star",
                    "page_size": 0,
                    "page_number": 1,
                    },
                {"status": 422},
            ),
        (
                {
                    "query": "The Star",
                    "page_size": 1000,
                    "page_number": 1,
                    },
                {"status": 422},
            ),
        (
                {
                    "query": "The Star",
                    "page_size": 10,
                    "page_number": 0,
                    },
                {"status": 422},
            ),
        (
                {
                    "query": "",
                    "page_size": 10,
                    "page_number": 1,
                    },
                {"status": 422},
            ),
        (
                {
                    "query": "  ",
                    "page_size": 10,
                    "page_number": 1,
                    },
                {"status": 200},
            ),
        (
                {
                    "query": "The Star",
                    "page_size": 10,
                    "page_number": -1,
                    },
                {"status": 422},
            ),
        ],
    )
@pytest.mark.asyncio
async def test_films_search_invalid_page(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    query_data,
    expected_answer,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(10, "The Star")
    bulk = make_bulk(docs)

    # 2. Загружаем данные в ES
    await es_write_data(bulk)

    # 3. Запрашиваем данные из ES по API
    url = test_settings.service_url + '/api/v1/films/search'
    query = {
        "query": query_data.get("query"),
        "page_size": query_data.get('page_size'),
        "page_number": query_data.get('page_number'),
        }

    body, status, _ = await make_get_request(url, query)
    assert status == expected_answer.get("status")


@pytest.mark.asyncio
async def test_films_search_cache_works(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(60, "The Star")
    bulk = make_bulk(docs)
    await es_write_data(bulk)

    # 2. Первый запрос — прогреваем кеш
    url = test_settings.service_url + '/api/v1/films/search'
    query = {"query": "The Star"}

    body, status, _ = await make_get_request(url, query)
    assert status == 200

    # 3. убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # 4. Второй запрос — должен прийти из кеша
    body, status, _ = await make_get_request(url, query)
    assert len(body['results']) == 50


@pytest.mark.asyncio
async def test_films_search_cache_expired_or_cleared(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    redis_flush,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(60, "The Star")
    bulk = make_bulk(docs)
    await es_write_data(bulk)

    # 2. Первый запрос — прогреваем кеш
    url = test_settings.service_url + '/api/v1/films/search'
    query = {"query": "The Star"}

    body, status, _ = await make_get_request(url, query)
    assert status == 200

    # 3. Сбрасываем кэш
    await redis_flush()

    # 4. убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # 5. Данных нет
    body, status, _ = await make_get_request(url, query)
    assert len(body['results']) == 0


@pytest.mark.asyncio
async def test_films_search_cache_isolation(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(60, "The Star")
    bulk = make_bulk(docs)
    await es_write_data(bulk)

    url = test_settings.service_url + '/api/v1/films/search'
    query = {"query": "The Star"}

    # 1. Первый запрос — прогреваем кеш
    body, status, _ = await make_get_request(url, query)
    assert status == 200

    # 2. Убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # 3. Новый запрос (другой query)
    query = {"query": "Matrix"}
    body, status, _ = await make_get_request(url, query)

    # кеша нет → даных нет
    assert len(body['results']) == 0


@pytest.mark.asyncio
async def test_films_search_cache_isolation_by_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    ):
    # 1. Генерируем данные для ES
    docs = generate_movies(60, "The Star")
    bulk = make_bulk(docs)
    await es_write_data(bulk)

    url = test_settings.service_url + '/api/v1/films/search'
    query = {"query": "The Star", "page_size": 10, "page_number": 1}

    # 1. Первый запрос — прогреваем кеш
    body, status, _ = await make_get_request(url, query)
    assert status == 200

    # 2. Убиваем ES
    await es_client.indices.delete(index=test_settings.es_index)

    # 3. # другой page_size → другой cache key
    query = {"query": "The Star", "page_size": 10, "page_number": 2}
    body, status, _ = await make_get_request(url, query)

    # кеша нет → даных нет
    assert len(body['results']) == 0


@pytest.mark.asyncio
async def test_films_search_missing_query(make_get_request):
    url = test_settings.service_url + '/api/v1/films/search'
    query = {
        "page_size": 10,
        "page_number": 1,
        }

    body, status, _ = await make_get_request(url, query)

    assert status == 422
