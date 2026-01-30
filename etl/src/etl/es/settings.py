from pydantic.v1 import BaseSettings


class EsSettings(BaseSettings):
    ES_HOST: str
    ES_PORT: int
    ES_INDEX: str

    class Config:
        env_file = ".env"
       