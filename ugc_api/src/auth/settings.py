from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    class ConfigDict:
        env_file = ".env"
        extra = "ignore"
