from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


ACCESS_TOKEN_LIFETIME_SECONDS = 24 * 60 * 60
ALGORITHM = "HS256"


def generate_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ACCESS_TOKEN_LIFETIME_SECONDS)).timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT returns str for algorithms >=2
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed("Invalid token") from exc


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Authentication class that authenticates using a Bearer JWT in the
    Authorization header. Never uses cookies.
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        auth_header: Optional[str] = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed("Invalid Authorization header format. Use 'Bearer <token>'")

        token = parts[1]
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Invalid token payload")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found") from exc

        if not user.is_active:
            # Treat inactive users as blocked
            raise AuthenticationFailed("User is blocked")

        return user, None
