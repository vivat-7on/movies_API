from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    es_host: str = Field(
        "http://127.0.0.1:9200", validation_alias="ES_HOST",
        )
    es_index: str = Field("movies", validation_alias="ES_INDEX")
    es_id_field: str = Field("id", validation_alias="ES_ID_FIELD")
    es_index_mapping: dict = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "imdb_id": {"type": "float"},
                "genres": {"type": "keyword"},
                "description": {"type": "text"},
                "directors": {"type": "keyword"},
                "actors_names": {"type": "keyword"},
                "writers_names": {"type": "keyword"},
                "actors": {"type": "keyword"},
                "writers": {"type": "date"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "keyword"},
                "film_work_type": {"type": "keyword"},
                },
            },
        }

    redis_host: str = Field("cache", validation_alias="REDIS_HOST")
    service_url: str = Field(
        "http://127.0.0.1:8000", validation_alias="SERVICE_URL",
        )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        )


test_settings = TestSettings()
