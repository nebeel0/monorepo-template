"""Example worker — demonstrates the BaseWorker pattern."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ExampleWorker(BaseWorker):
    """Example background worker that runs periodically.

    Replace this with your actual worker logic (cleanup tasks,
    notifications, data processing, etc.)
    """

    def __init__(self, interval_seconds: int = 300):
        super().__init__(name="example", interval_seconds=interval_seconds)

    async def process(self, session: AsyncSession) -> None:
        logger.debug("ExampleWorker tick")
