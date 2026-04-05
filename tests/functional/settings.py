from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    es_host: str = Field(
        "127.0.0.1",
        validation_alias="ES_HOST",
    )
    es_port: int = Field(9200, validation_alias="ES_PORT")
    es_index: str = Field("movies", validation_alias="ES_INDEX")
    es_id_field: str = Field("id", validation_alias="ES_ID_FIELD")

    redis_host: str = Field("127.0.0.1", validation_alias="REDIS_HOST")
    redis_port: int = 6379
    service_url: str = Field(
        "http://127.0.0.1:8000",
        validation_alias="SERVICE_URL",
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


test_settings = TestSettings()
