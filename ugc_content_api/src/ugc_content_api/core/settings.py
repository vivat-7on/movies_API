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
        extra="ignore",
    )


class AuthSettings(BaseSettings):
    JWT_PUBLIC_KEY_PATH: Path
    JWT_ALGORITHM: str = "RS256"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    @property
    def jwt_public_key(self) -> str:
        return self.JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()  # type: ignore[call-arg]


@lru_cache
def get_mongo_settings() -> MongoSettings:
    return MongoSettings()
