import logging
from collections.abc import Iterable

from aiogram import Bot

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot | None = None):
        self.bot = bot

    async def notify_managers(self, manager_ids: Iterable[int], text: str) -> None:
        if not self.bot:
            logger.warning("Notification bot is not configured")
            return

        for manager_id in manager_ids:
            try:
                await self.bot.send_message(manager_id, text)
            except Exception:
                logger.exception("Failed to notify manager %s", manager_id)

    async def notify_client(self, telegram_id: int, text: str) -> None:
        if not self.bot:
            logger.warning("Notification bot is not configured")
            return

        try:
            await self.bot.send_message(telegram_id, text)
        except Exception:
            logger.exception("Failed to notify client %s", telegram_id)
