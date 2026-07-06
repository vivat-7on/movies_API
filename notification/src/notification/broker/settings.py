from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class RabbitSettings(BaseSettings):
    RABBIT_HOST: str = "127.0.0.1"
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASS: str = "guest"
    RABBIT_VHOST: str = "/"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    @property
    def dsn(self) -> str:
        return (
            f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASS}"
            f"@{self.RABBIT_HOST}:{self.RABBIT_PORT}{self.RABBIT_VHOST}"
        )
