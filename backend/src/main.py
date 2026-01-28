from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core import config
from core.config import setup_logging
from db import elastic, redis

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=False,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}']
    )
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
