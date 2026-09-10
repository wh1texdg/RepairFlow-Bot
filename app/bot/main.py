import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.core.config import settings
from app.core.logging import setup_logging


async def main():
    setup_logging(settings.log_level)

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured")

    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
