import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.testdata import MAPPING_MOVIES

BASE_URL = test_settings.service_url + "/api/v1/films"


@pytest.mark.asyncio
async def test_film_list_basic(
    es_write_data,
    make_get_request,
    generate_movies,
    make_bulk,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": 1,
    }
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == 200
    assert len(body["results"]) == 50
    assert body["count"] == 60


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "page_number": 1,
                "page_size": 30,
            },
            {
                "status": 200,
                "length": 30,
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
async def test_film_list_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
    }
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == expected_answer.get("status")
    assert len(body["results"]) == expected_answer.get("length")
    assert body["count"] == 60


@pytest.mark.asyncio
async def test_film_list_default_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {}
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == 200
    assert len(body["results"]) == 50
    assert body["count"] == 60


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
                "page_size": 20,
            },
            {
                "status": 422,
            },
        ),
        (
            {
                "page_number": -1,
                "page_size": 20,
            },
            {
                "status": 422,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_list_invalid_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    query_data,
    expected_answer,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": query_data.get("page_number"),
        "page_size": query_data.get("page_size"),
    }
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == expected_answer.get("status")


@pytest.mark.asyncio
async def test_film_list_sort_rating_asc(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
):
    es_data = generate_movies(1, "The Star", rating=1.0)
    for r in range(2, 11):
        es_data.extend(generate_movies(1, "The Star", rating=float(r)))
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": 1,
        "page_size": 5,
        "sort": "imdb_rating",
    }
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == 200
    assert len(body["results"]) == 5
    assert body["count"] == 10

    rating = [film["imdb_rating"] for film in body["results"]]
    assert sorted(rating) == rating
    assert rating == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_film_list_sort_rating_desc(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
):
    es_data = generate_movies(1, "The Star", rating=1.0)
    for r in range(2, 11):
        es_data.extend(generate_movies(1, "The Star", rating=float(r)))
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": 1,
        "page_size": 5,
        "sort": "-imdb_rating",
    }
    body, status, _ = await make_get_request(BASE_URL, query)

    assert status == 200
    assert len(body["results"]) == 5
    assert body["count"] == 10

    rating = [film["imdb_rating"] for film in body["results"]]
    assert sorted(rating, reverse=True) == rating
    assert rating == [10, 9, 8, 7, 6]


@pytest.mark.asyncio
async def test_film_list_filter_by_genre(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
):
    genre_ids = [
        "37d69fa5-12ed-4d93-b48e-edf57161dfa6",
        "8d1182d4-1d58-483e-b159-2212de046575",
        "59015f5d-387d-45ae-8d78-31e17f71451c",
        "87dd2b84-3cfe-4479-975c-a6af7f60e545",
        "f36376b4-4c1a-46c6-a3fd-2fe0dd2a76fe",
    ]
    genre_names = [
        "Action",
        "Adventure",
        "Animation",
        "Sci-Fi",
        "Horror",
    ]
    film_ids = [
        "bbeb6129-152f-4d1b-9869-8046e33be03b",
        "85c8bcdc-ca7c-4dd5-b881-18fce0243f1f",
        "b06e90ac-c57c-4ca8-a457-bf395f0ee81a",
        "2439c35a-11ec-4177-9291-ad51a44ce76c",
        "46cff8ba-f2c7-4773-b8e1-4be6d0b48a8c",
    ]

    es_data = []
    for id, name, film in zip(genre_ids, genre_names, film_ids, strict=True):
        genres = []
        genres.append(
            {
                "id": id,
                "name": name,
            },
        )
        es_data.extend(
            generate_movies(
                count=1,
                title="The Star",
                film_id=film,
                genres=genres,
            ),
        )

    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    for genre, film in zip(genre_ids, film_ids, strict=True):
        query = {
            "genre": genre,
        }
        body, status, _ = await make_get_request(BASE_URL, query)
        ids = [film["uuid"] for film in body["results"]]

        assert status == 200
        assert film in ids


@pytest.mark.asyncio
async def test_film_list_cache_works(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {
        "page_number": 1,
        "page_size": 50,
    }

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200

    await es_client.indices.delete(index=test_settings.es_index)

    body, status, _ = await make_get_request(BASE_URL, query)
    assert len(body["results"]) == 50


@pytest.mark.asyncio
async def test_film_list_cache_isolation_pagination(
    es_write_data,
    generate_movies,
    make_bulk,
    make_get_request,
    es_client,
):
    es_data = generate_movies(60, "The Star")
    bulk = make_bulk(
        docs=es_data,
        index="movies",
    )
    await es_write_data(
        index="movies",
        mapping=MAPPING_MOVIES,
        data=bulk,
    )

    query = {"page_number": 1}

    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200

    await es_client.indices.delete(index=test_settings.es_index)

    body, status, _ = await make_get_request(BASE_URL, query)
    assert len(body["results"]) == 50
    assert body["count"] == 60

    query = {"page_number": 2}
    body, status, _ = await make_get_request(BASE_URL, query)
    assert status == 200
    assert body["results"] == []
