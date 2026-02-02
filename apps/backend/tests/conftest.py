import uuid
from collections.abc import AsyncGenerator
from functools import cache

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from core.config import settings
from core.database import get_app_db_session, get_users_db_session
from core.schemas.base import AppDBModel, UserManagementDBModel


# ---------------------------------------------------------------------------
# Test database engines (use separate schemas for isolation)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app_db_engine():
    return create_async_engine(settings.APP_DB_URL, echo=False)


@pytest.fixture(scope="session")
def users_db_engine():
    return create_async_engine(settings.USERS_DB_URL, echo=False)


# ---------------------------------------------------------------------------
# Per-test schema isolation
# ---------------------------------------------------------------------------


@pytest.fixture
async def app_db_session(app_db_engine) -> AsyncGenerator[AsyncSession, None]:
    schema_name = f"test_{uuid.uuid4().hex[:8]}"
    async with app_db_engine.connect() as conn:
        await conn.execute(type(conn).text(f'CREATE SCHEMA "{schema_name}"'))
        await conn.execute(type(conn).text(f'SET search_path TO "{schema_name}"'))
        await conn.run_sync(AppDBModel.metadata.create_all)
        await conn.commit()

    session_maker = async_sessionmaker(bind=app_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        await session.execute(type(session).text(f'SET search_path TO "{schema_name}"'))
        yield session

    async with app_db_engine.connect() as conn:
        await conn.execute(type(conn).text(f'DROP SCHEMA "{schema_name}" CASCADE'))
        await conn.commit()


@pytest.fixture
async def users_db_session(users_db_engine) -> AsyncGenerator[AsyncSession, None]:
    schema_name = f"test_{uuid.uuid4().hex[:8]}"
    async with users_db_engine.connect() as conn:
        await conn.execute(type(conn).text(f'CREATE SCHEMA "{schema_name}"'))
        await conn.execute(type(conn).text(f'SET search_path TO "{schema_name}"'))
        await conn.run_sync(UserManagementDBModel.metadata.create_all)
        await conn.commit()

    session_maker = async_sessionmaker(bind=users_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        await session.execute(type(session).text(f'SET search_path TO "{schema_name}"'))
        yield session

    async with users_db_engine.connect() as conn:
        await conn.execute(type(conn).text(f'DROP SCHEMA "{schema_name}" CASCADE'))
        await conn.commit()


# ---------------------------------------------------------------------------
# HTTP client with dependency overrides
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(app_db_session, users_db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_app_db():
        yield app_db_session

    async def override_users_db():
        yield users_db_session

    app.dependency_overrides[get_app_db_session] = override_app_db
    app.dependency_overrides[get_users_db_session] = override_users_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Cache cleanup
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all @cache decorated functions between tests."""
    yield
    for obj in [
        *[
            getattr(mod, name)
            for mod_name in ["core.database"]
            for mod in [__import__(mod_name, fromlist=[""])]
            for name in dir(mod)
            if callable(getattr(mod, name)) and hasattr(getattr(mod, name), "cache_clear")
        ],
    ]:
        obj.cache_clear()
