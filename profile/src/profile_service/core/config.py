from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class AuthSettings(BaseSettings):
    JWT_PUBLIC_KEY_PATH: Path
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    @property
    def jwt_public_key_path(self) -> str:
        return self.JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")


class AppSettings(BaseSettings):
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()  # type: ignore[call-arg]
