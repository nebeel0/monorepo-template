from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager
from functools import cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings


# ---------------------------------------------------------------------------
# Engine factories (cached singletons)
# ---------------------------------------------------------------------------


@cache
def get_app_db_engine() -> AsyncEngine:
    return create_async_engine(
        settings.APP_DB_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


@cache
def get_users_db_engine() -> AsyncEngine:
    return create_async_engine(
        settings.USERS_DB_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


# ---------------------------------------------------------------------------
# Session factories
# ---------------------------------------------------------------------------


@cache
def get_app_db_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_app_db_engine(), class_=AsyncSession, expire_on_commit=False
    )


@cache
def get_users_db_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_users_db_engine(), class_=AsyncSession, expire_on_commit=False
    )


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


async def get_app_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_app_db_session_maker()
    async with session_maker() as session:
        yield session


async def get_users_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_users_db_session_maker()
    async with session_maker() as session:
        yield session


AppDbSessionDep = Annotated[AsyncSession, Depends(get_app_db_session)]
UsersDbSessionDep = Annotated[AsyncSession, Depends(get_users_db_session)]


# ---------------------------------------------------------------------------
# PostgresProvider (lifecycle management)
# ---------------------------------------------------------------------------


class PostgresProvider(AbstractAsyncContextManager):
    """Manages engine + session lifecycle for graceful shutdown."""

    def __init__(self, engine: AsyncEngine, session_maker: async_sessionmaker[AsyncSession]):
        self.engine = engine
        self.session_maker = session_maker
        self._active_sessions: list[AsyncSession] = []

    async def __aenter__(self) -> "PostgresProvider":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.cleanup()

    async def create_session(self) -> AsyncSession:
        session = self.session_maker()
        self._active_sessions.append(session)
        return session

    async def cleanup(self) -> None:
        for session in self._active_sessions:
            if session.is_active:
                await session.close()
        await self.engine.dispose()
