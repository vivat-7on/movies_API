from pydantic.v1 import BaseSettings


class DBSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    class Config:
        env_file = ".env"
