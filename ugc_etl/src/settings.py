from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    KAFKA_HOST: str = "kafka"
    KAFKA_PORT: int = 9092
    KAFKA_TOPIC: str = "events"
    KAFKA_GROUP_ID: str = "ugc-etl"

    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_DB: str = "movies"
    CLICKHOUSE_TABLE: str = "events"
    CLICKHOUSE_PASSWORD: str = "password"

    BATCH_SIZE: int = 10
    BATCH_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = BASE_DIR.parent / ".env"
        extra = "ignore"

    @property
    def kafka_bootstrap_servers(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"
