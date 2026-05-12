import http

import httpx
from attr import frozen
from pydantic import ValidationError

from auth.core.config import YandexAuthSettings
from auth.dtos.token import YandexTokensDTO, YandexUserInfoDTO


@frozen
class YandexClient:
    yandex_auth_settings: YandexAuthSettings

    async def exchange_code_for_token(
        self,
        code: str,
    ) -> YandexTokensDTO | None:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    self.yandex_auth_settings.YANDEX_TOKEN_URI,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": (self.yandex_auth_settings.YANDEX_REDIRECT_URI),
                    },
                    auth=(
                        self.yandex_auth_settings.YANDEX_CLIENT_ID,
                        self.yandex_auth_settings.YANDEX_CLIENT_SECRET,
                    ),
                )
        except httpx.HTTPError:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        return YandexTokensDTO(**response.json())

    async def get_user_info(
        self,
        yandex_token: str,
    ) -> YandexUserInfoDTO | None:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    self.yandex_auth_settings.YANDEX_USER_INFO_URI,
                    params={"format": "json"},
                    headers={"Authorization": f"OAuth {yandex_token}"},
                )
        except httpx.HTTPError:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None
        try:
            return YandexUserInfoDTO(**response.json())
        except (ValueError, ValidationError):
            return None
