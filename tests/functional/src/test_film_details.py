import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
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
async def test_film_get_by_id(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
    query_data,
    expected_answer,
    ):
    film_id = query_data.get("film_id")
    search_film_id = query_data.get("search_film_id")

    docs = generate_movies(1, "The Star", film_id)
    bulk = make_bulk(docs)
    await es_write_data(bulk)

    url = test_settings.service_url + '/api/v1/films/{}'.format(search_film_id)
    query = {}
    body, status, _ = await make_get_request(url, query)
    assert status == expected_answer.get("status_code")
    if status == 200:
        assert body["uuid"] == expected_answer.get("request_film_id")
