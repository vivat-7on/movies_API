from pathlib import Path

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    JWT_PUBLIC_KEY_PATH: Path
    JWT_ALGORITHM: str = "RS256"

    class ConfigDict:
        env_file = ".env"
        extra = "ignore"

    @property
    def jwt_public_key_path(self) -> str:
        return self.JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")
