from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        name: str | None = None,
        phone: str | None = None,
    ):
        return await self.repo.get_or_create(
            telegram_id=telegram_id,
            username=username,
            name=name,
            phone=phone,
        )
