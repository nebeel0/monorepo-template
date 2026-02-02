"""Base worker class for periodic background tasks."""

import asyncio
import contextlib
import logging
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_app_db_session_maker

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Base class for background workers.

    Provides:
    - Periodic execution at a configurable interval
    - Database session management per iteration
    - Error handling and logging
    - Graceful shutdown
    """

    def __init__(self, name: str, interval_seconds: int = 60):
        self.name = name
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._running:
            logger.warning("Worker %s already running", self.name)
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Worker %s started (interval=%ds)", self.name, self.interval_seconds)

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        logger.info("Worker %s stopped", self.name)

    async def _run_loop(self) -> None:
        while self._running:
            try:
                session_maker = get_app_db_session_maker()
                async with session_maker() as session:
                    await self.process(session)
                    await session.commit()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Worker %s error", self.name)
            await asyncio.sleep(self.interval_seconds)

    @abstractmethod
    async def process(self, session: AsyncSession) -> None:
        """Process a single iteration. Override in subclasses."""

    async def run_once(self) -> Any:
        """Run a single iteration (for testing or manual triggers)."""
        session_maker = get_app_db_session_maker()
        async with session_maker() as session:
            result = await self.process(session)
            await session.commit()
            return result
