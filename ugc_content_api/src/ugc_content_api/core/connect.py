from pymongo import AsyncMongoClient

from ugc_content_api.core.settings import MongoSettings


def create_client(settings: MongoSettings) -> AsyncMongoClient:
    client: AsyncMongoClient = AsyncMongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
    )
    return client
