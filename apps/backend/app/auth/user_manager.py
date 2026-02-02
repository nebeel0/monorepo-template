import logging
import uuid
from functools import cache
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from httpx_oauth.clients.google import GoogleOAuth2

from core.config import settings
from core.schemas.users import OAuthAccount, User

logger = logging.getLogger(__name__)


@cache
def get_google_oauth_client() -> GoogleOAuth2:
    return GoogleOAuth2(
        settings.GOOGLE_OAUTH_CLIENT_ID,
        settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        logger.info("User %s has registered.", user.id)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info("User %s forgot password. Token: %s", user.id, token)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info("Verification requested for user %s. Token: %s", user.id, token)
