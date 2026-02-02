import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    RedisStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.user_manager import UserManager
from core.config import settings
from core.database import get_users_db_session
from core.schemas.users import OAuthAccount, User

# ---------------------------------------------------------------------------
# User DB adapter
# ---------------------------------------------------------------------------


async def get_user_db(
    session: AsyncSession = Depends(get_users_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[Any, Any], None]:
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


# ---------------------------------------------------------------------------
# User manager
# ---------------------------------------------------------------------------


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[Any, Any] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


# ---------------------------------------------------------------------------
# Transport layers
# ---------------------------------------------------------------------------

# Bearer token transport (mobile apps)
bearer_transport = BearerTransport(tokenUrl="auth/login")

# Cookie transport (web apps)
TOKEN_LIFETIME = settings.JWT_LIFETIME_SECONDS
cookie_transport = CookieTransport(
    cookie_name=f"{settings.APP_NAME}_auth",
    cookie_max_age=TOKEN_LIFETIME,
    cookie_secure=not settings.IS_LOCAL,
    cookie_httponly=True,
    cookie_samesite="lax",
)

# ---------------------------------------------------------------------------
# Strategy (Redis-backed sessions)
# ---------------------------------------------------------------------------

redis_instance = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:  # type: ignore[type-arg]
    return RedisStrategy(redis_instance, lifetime_seconds=TOKEN_LIFETIME)


# ---------------------------------------------------------------------------
# Authentication backends
# ---------------------------------------------------------------------------

redis_auth_backend = AuthenticationBackend(
    name="redis_bearer",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

cookie_auth_backend = AuthenticationBackend(
    name="redis_cookie",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)

# ---------------------------------------------------------------------------
# FastAPIUsers instance
# ---------------------------------------------------------------------------

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [redis_auth_backend, cookie_auth_backend],
)

# Dependency shortcuts
current_user = fastapi_users.current_user()
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
