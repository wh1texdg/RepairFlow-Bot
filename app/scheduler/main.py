from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import remind_stale_requests


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        remind_stale_requests,
        trigger="cron",
        hour=10,
        minute=0,
        id="stale_requests_reminder",
        replace_existing=True,
    )
    return scheduler
