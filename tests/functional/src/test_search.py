import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star'},
                {'status': 200, 'length': 50},
            ),
        (
                {'query': 'Mashed potato'},
                {'status': 200, 'length': 0},
            ),
        ],
    )
@pytest.mark.asyncio
async def test_search(
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
    assert status == 200

    # 4. Проверяем ответ
    assert status == expected_answer.get('status')
    assert len(body['results']) == expected_answer.get('length')


@pytest.mark.asyncio
async def test_search_cache_works(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    query_data,
    ):
    # 1. Генерируем данные для ES
    es_data = generate_movies(60, "The Star")
    bulk_query = make_bulk(es_data)

    # 2. Загружаем данные в ES
    await es_write_data(bulk_query)

    # 3. Запрашиваем данные из ES по API
    url = test_settings.service_url + '/api/v1/films/search'
    body, status, _ = await make_get_request(url, query_data)
    assert status == 200
