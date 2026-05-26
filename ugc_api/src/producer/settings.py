from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = 9092
    KAFKA_TOPIC: str = "events"

    class Config:
        env_file = ".env"

    @property
    def kafka_bootstrap_servers(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"
