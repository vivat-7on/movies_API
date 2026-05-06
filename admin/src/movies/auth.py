import http

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(
        self,
        request,
        username=None,
        password=None,
    ) -> User | None:
        if not username or not password:
            return None

        login_url = settings.AUTH_API_LOGIN_URL
        payload = {"login": username, "password": password}
        timeout = settings.AUTH_API_TIMEOUT
        try:
            response = requests.post(login_url, json=payload, timeout=timeout)
        except requests.RequestException:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        keys = response.json()
        access_token = keys.get("access_token", None)
        if access_token is None:
            return None

        auth_url = settings.AUTH_API_ME_URL

        try:
            me_response = requests.get(
                auth_url,
                timeout=timeout,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except requests.RequestException:
            return None

        if me_response.status_code != http.HTTPStatus.OK:
            return None
        try:
            data = me_response.json()
        except ValueError:
            return None

        roles = data.get("roles", [])
        if "admin" not in roles:
            return None

        try:
            user, _ = User.objects.get_or_create(
                id=data["user_id"],
                defaults={"login": username},
            )
            user.login = username
            user.is_admin = True
            user.is_active = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id: str) -> User | None:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
