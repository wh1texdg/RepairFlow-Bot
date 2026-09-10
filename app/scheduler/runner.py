import asyncio

from app.core.config import settings
from app.core.logging import setup_logging
from app.scheduler.main import build_scheduler


async def main():
    setup_logging(settings.log_level)
    scheduler = build_scheduler()
    scheduler.start()
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
