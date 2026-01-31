from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi.params import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from repositories.cache.film_cache import FilmCacheRepository
from repositories.cache.genre_cache import GenreCacheRepository
from repositories.cache.person_cache import PersonCacheRepository
from repositories.elastic.film_elastic import FilmElasticRepository
from repositories.elastic.genre_elastic import GenreElasticRepository
from repositories.elastic.person_elastic import PersonElasticRepository
from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService


def create_film_elastic_repository(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> FilmElasticRepository:
    return FilmElasticRepository(elastic=elastic)


def create_film_cache_repository(
    redis: Redis = Depends(get_redis),
    ) -> FilmCacheRepository:
    return FilmCacheRepository(redis=redis)


@lru_cache()
def create_film_service(
    elastic_repo: FilmElasticRepository = Depends(
        create_film_elastic_repository,
        ),
    cache_repo: FilmCacheRepository = Depends(create_film_cache_repository),
    ) -> FilmService:
    return FilmService(
        elastic_repo=elastic_repo,
        cache_repo=cache_repo,
        )


def create_genre_elastic_repository(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> GenreElasticRepository:
    return GenreElasticRepository(elastic=elastic)


def create_genre_cache_repository(
    redis: Redis = Depends(get_redis),
    ) -> GenreCacheRepository:
    return GenreCacheRepository(redis=redis)


@lru_cache()
def create_genre_service(
    elastic_repo: GenreElasticRepository = Depends(
        create_genre_elastic_repository,
        ),
    cache_repo: GenreCacheRepository = Depends(create_genre_cache_repository),
    ) -> GenreService:
    return GenreService(
        elastic_repo=elastic_repo,
        cache_repo=cache_repo,
        )


def create_person_elastic_repository(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> PersonElasticRepository:
    return PersonElasticRepository(elastic=elastic)


def create_person_cache_repository(
    redis: Redis = Depends(get_redis),
    ) -> PersonCacheRepository:
    return PersonCacheRepository(redis=redis)


@lru_cache()
def create_person_service(
    elastic_repo: PersonElasticRepository = Depends(
        create_person_elastic_repository,
        ),
    cache_repo: PersonCacheRepository = Depends(create_person_cache_repository),
    ) -> PersonService:
    return PersonService(
        elastic_repo=elastic_repo,
        cache_repo=cache_repo,
        )
