from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi.params import Depends
from redis import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from repositories.film_cache import FilmCacheRepository
from repositories.film_elastic import FilmElasticRepository
from services.film import FilmService


def create_film_elastic_repository(
    elastic: AsyncElasticsearch=Depends(get_elastic),
) -> FilmElasticRepository:
    return FilmElasticRepository(elastic=elastic)

def create_film_cache_repository(
    redis: Redis=Depends(get_redis),
) -> FilmCacheRepository:
    return FilmCacheRepository(redis=redis)

@lru_cache()
def create_film_service(
    elastic: FilmElasticRepository = Depends(create_film_elastic_repository),
    redis: FilmCacheRepository = Depends(create_film_cache_repository),
) -> FilmService:
    return FilmService(
        elastic_repo=elastic,
        cache_repo=redis,
    )
