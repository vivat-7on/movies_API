from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class AuthSettings(BaseSettings):
    AUTH_BASE_URL: str = "http://localhost:8000/api/v1"
    AUTH_USER_URL: str = "/users/{user_id}"
    AUTH_SERVICE_TOKEN: str = "your_service_token"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    @property
    def url(self):
        return self.AUTH_BASE_URL + self.AUTH_USER_URL
