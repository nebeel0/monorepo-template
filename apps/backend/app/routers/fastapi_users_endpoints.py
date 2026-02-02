from fastapi import FastAPI

from app.auth.user_manager import get_google_oauth_client
from app.dependencies.auth import (
    cookie_auth_backend,
    fastapi_users,
    redis_auth_backend,
)
from app.models.user import UserRead, UserUpdate
from core.config import settings


def add_fastapi_endpoints(app: FastAPI) -> None:
    """Register all fastapi-users authentication and user management endpoints."""
    google_client = get_google_oauth_client()
    auth_secret = settings.SECRET

    # Google OAuth — bearer token flow (mobile)
    if settings.GOOGLE_OAUTH_CLIENT_ID:
        app.include_router(
            fastapi_users.get_oauth_router(
                google_client,
                redis_auth_backend,
                auth_secret,
                associate_by_email=True,
                is_verified_by_default=True,
            ),
            prefix="/auth/google-bearer",
            tags=["auth"],
        )

        # Google OAuth — cookie flow (web)
        app.include_router(
            fastapi_users.get_oauth_router(
                google_client,
                cookie_auth_backend,
                auth_secret,
                associate_by_email=True,
                is_verified_by_default=True,
            ),
            prefix="/auth/google-cookie",
            tags=["auth"],
        )

        # OAuth account association
        app.include_router(
            fastapi_users.get_oauth_associate_router(
                google_client,
                UserRead,
                auth_secret,
            ),
            prefix="/auth/associate/google",
            tags=["auth"],
        )

    # Cookie-based auth (web login/logout)
    app.include_router(
        fastapi_users.get_auth_router(cookie_auth_backend),
        prefix="/users/cookie",
        tags=["users"],
    )

    # Bearer token auth (mobile login/logout)
    app.include_router(
        fastapi_users.get_auth_router(redis_auth_backend),
        prefix="/users/token",
        tags=["users"],
    )

    # User management
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
