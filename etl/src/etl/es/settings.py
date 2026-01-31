from pydantic.v1 import BaseSettings


class EsSettings(BaseSettings):
    ES_HOST: str
    ES_PORT: int
    MOVIES_ES_INDEX: str
    GENRES_ES_INDEX: str
    PERSONS_ES_INDEX: str

    class Config:
        env_file = ".env"
