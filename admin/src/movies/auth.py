import http
import logging
import uuid

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

logger = logging.getLogger(__name__)
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
            x_request_id = (
                request.headers.get("X-Request-Id") if request is not None else None
            ) or str(uuid.uuid4())
            response = requests.post(
                login_url,
                json=payload,
                timeout=timeout,
                headers={"X-Request-Id": x_request_id},
            )
        except requests.RequestException:
            logger.exception("Auth login request failed")
            return None

        if response.status_code != http.HTTPStatus.OK:
            logger.warning(
                "Auth login rejected: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None
        try:
            keys = response.json()
        except ValueError:
            logger.warning("Auth login returned invalid JSON")
            return None

        access_token = keys.get("access_token", None)
        if access_token is None:
            logger.warning("Auth login response has no access_token")
            return None

        auth_url = settings.AUTH_API_ME_URL

        try:
            me_response = requests.get(
                auth_url,
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Request-Id": x_request_id,
                },
            )
        except requests.RequestException:
            logger.exception("Auth user request failed")
            return None

        if me_response.status_code != http.HTTPStatus.OK:
            logger.warning(
                "Auth user request rejected: status=%s body=%s",
                me_response.status_code,
                me_response.text,
            )
            return None
        try:
            data = me_response.json()
        except ValueError:
            logger.warning("Auth user response has invalid JSON")
            return None

        roles = data.get("roles", [])
        if "admin" not in roles:
            logger.warning(
                "User %s has no admin role: %s",
                username,
                roles,
            )
            return None

        try:
            user, _ = User.objects.update_or_create(
                id=data["user_id"],
                defaults={"login": username},
            )
            user.login = username
            user.is_admin = True
            user.is_active = True
            user.save()
        except Exception:
            logger.exception("Failed to synchronize admin user")
            return None

        return user

    def get_user(self, user_id: str) -> User | None:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
