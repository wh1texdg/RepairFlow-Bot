from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import UserRole
from app.database.models.manager import Manager


class ManagerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Manager | None:
        result = await self.session.execute(
            select(Manager).where(Manager.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, manager_id: int) -> Manager | None:
        return await self.session.get(Manager, manager_id)

    async def create(
        self,
        telegram_id: int,
        name: str,
        role: UserRole = UserRole.MANAGER,
    ) -> Manager:
        manager = Manager(telegram_id=telegram_id, name=name, role=role)
        self.session.add(manager)
        await self.session.flush()
        return manager

    async def get_active(self) -> list[Manager]:
        result = await self.session.execute(
            select(Manager).where(Manager.is_active.is_(True))
        )
        return list(result.scalars().all())
