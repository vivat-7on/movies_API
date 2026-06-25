from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class MongoSettings(BaseSettings):
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "ugc_content_api"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
    )


@lru_cache
def get_mongo_settings() -> MongoSettings:
    return MongoSettings()
