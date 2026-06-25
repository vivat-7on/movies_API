from typing import AsyncGenerator

from fastapi import Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.core.settings import MongoSettings, get_mongo_settings


async def get_mongo_db(
    settings: MongoSettings = Depends(get_mongo_settings),
) -> AsyncGenerator[AsyncDatabase, None]:
    client = AsyncMongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
    )
    try:
        yield client[settings.MONGO_DB]
    finally:
        await client.close()
