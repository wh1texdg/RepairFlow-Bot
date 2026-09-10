import logging

from aiogram import Bot

from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.integrations.notifications import NotificationService
from app.repositories.request_repository import RequestRepository

logger = logging.getLogger(__name__)


async def remind_stale_requests() -> None:
    async with AsyncSessionLocal() as session:
        requests = await RequestRepository(session).get_stale_new(hours=24)

    if not requests or not settings.bot_token:
        return

    bot = Bot(settings.bot_token)
    try:
        notifier = NotificationService(bot)
        text = "Напоминание: есть заявки NEW старше 24 часов.\n"
        text += "\n".join(f"#{request.id} — {request.city}, {request.address}" for request in requests)
        await notifier.notify_managers(settings.manager_telegram_ids, text)
    finally:
        await bot.session.close()
