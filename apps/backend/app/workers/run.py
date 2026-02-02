"""Standalone worker runner — starts all background workers outside of the web process."""

import asyncio
import signal

from app.workers.example import ExampleWorker
from core.logging import setup_logging


async def main() -> None:
    setup_logging()
    print("Starting background workers...")

    workers = [
        ExampleWorker(interval_seconds=60),
        # Add more workers here:
        # CleanupWorker(interval_seconds=3600),
        # NotificationWorker(interval_seconds=300),
    ]

    shutdown_event = asyncio.Event()

    def handle_shutdown(signum: int, frame: object) -> None:
        print("\nShutdown signal received, stopping workers...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    for worker in workers:
        await worker.start()
        print(f"  Started: {worker.__class__.__name__} (interval={worker.interval_seconds}s)")

    print(f"\n{len(workers)} worker(s) running. Press Ctrl+C to stop.\n")
    await shutdown_event.wait()

    for worker in workers:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
