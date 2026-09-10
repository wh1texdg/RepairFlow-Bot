import asyncio
import sys

from app.core.logging import setup_logging
from app.database.models.enums import UserRole
from app.database.session import AsyncSessionLocal
from app.repositories.manager_repository import ManagerRepository


async def main():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python -m app.scripts.seed_manager TELEGRAM_ID NAME [ADMIN]")

    telegram_id = int(sys.argv[1])
    name = sys.argv[2]
    role = UserRole.ADMIN if len(sys.argv) > 3 and sys.argv[3].upper() == "ADMIN" else UserRole.MANAGER

    setup_logging()
    async with AsyncSessionLocal() as session:
        repo = ManagerRepository(session)
        manager = await repo.get_by_telegram_id(telegram_id)
        if manager:
            manager.name = name
            manager.role = role
            manager.is_active = True
        else:
            manager = await repo.create(telegram_id, name, role)
        await session.commit()
        print(f"Manager ready: id={manager.id}, telegram_id={manager.telegram_id}, role={manager.role}")


if __name__ == "__main__":
    asyncio.run(main())
