from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def create(
        self,
        telegram_id: int,
        username: str | None = None,
        name: str | None = None,
        phone: str | None = None,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            name=name,
            phone=phone,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        name: str | None = None,
        phone: str | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            changed = False
            if username is not None and user.username != username:
                user.username = username
                changed = True
            if name is not None and user.name != name:
                user.name = name
                changed = True
            if phone is not None and user.phone != phone:
                user.phone = phone
                changed = True
            if changed:
                await self.session.flush()
            return user
        return await self.create(telegram_id, username, name, phone)
