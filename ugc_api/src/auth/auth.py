import uuid

from jose import jwt

from .settings import AuthSettings


class Auth:
    def __init__(self, settings: AuthSettings):
        self.settings = settings

    def get_user_id_from_token(
        self,
        auth_header: str | None,
    ) -> uuid.UUID | None:
        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            raise ValueError("Invalid Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()

        payload = jwt.decode(
            token,
            key=self.settings.jwt_public_key_path,
            algorithms=[self.settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token does not contain user_id")

        return uuid.UUID(user_id)
