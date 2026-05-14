from typing import Protocol

from auth.dtos.token import OAuthUserInfoDTO


class IOAuthProvider(Protocol):
    name: str

    def get_authorize_url(self, state: str) -> str: ...

    async def get_user_info_by_code(self, code: str) -> OAuthUserInfoDTO: ...
