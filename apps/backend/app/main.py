import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.routers.fastapi_users_endpoints import add_fastapi_endpoints
from app.routers.service_endpoints import add_service_endpoints
from core.config import settings
from core.database import get_app_db_engine, get_users_db_engine
from core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("Starting %s", settings.APP_NAME)

    # Start workers (import here to avoid circular imports)
    from app.workers.example import ExampleWorker

    worker = ExampleWorker()
    await worker.start()

    yield

    # Shutdown
    await worker.stop()
    await get_app_db_engine().dispose()
    await get_users_db_engine().dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.IS_LOCAL else None,
    redoc_url="/redoc" if settings.IS_LOCAL else None,
)

# CORS
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if settings.IS_LOCAL:
    cors_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes (fastapi-users)
add_fastapi_endpoints(app)

# Dynamic API routes
add_service_endpoints(app)


# ---------------------------------------------------------------------------
# Health check with dependency verification
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> Response:
    checks: dict[str, str] = {}

    # Check app DB
    try:
        engine = get_app_db_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["app_db"] = "ok"
    except Exception:
        checks["app_db"] = "error"

    # Check users DB
    try:
        engine = get_users_db_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["users_db"] = "ok"
    except Exception:
        checks["users_db"] = "error"

    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503

    from fastapi.responses import JSONResponse

    return JSONResponse(
        content={"status": "ok" if all_ok else "degraded", **checks},
        status_code=status_code,
    )
