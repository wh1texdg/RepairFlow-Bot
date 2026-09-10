from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import RequestStatus
from app.database.models.request import Request
from app.database.models.status_history import RequestStatusHistory


class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **data) -> Request:
        request = Request(**data)
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_by_id(self, request_id: int) -> Request | None:
        return await self.session.get(Request, request_id)

    async def get_by_user(self, user_id: int) -> list[Request]:
        result = await self.session.execute(
            select(Request)
            .where(Request.user_id == user_id)
            .order_by(Request.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(
        self,
        status: RequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Request]:
        query = select(Request).order_by(Request.created_at.desc()).limit(limit).offset(offset)
        if status:
            query = query.where(Request.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_history(self, request_id: int) -> list[RequestStatusHistory]:
        result = await self.session.execute(
            select(RequestStatusHistory)
            .where(RequestStatusHistory.request_id == request_id)
            .order_by(RequestStatusHistory.created_at)
        )
        return list(result.scalars().all())

    async def add_history(
        self,
        request_id: int,
        old_status: RequestStatus | None,
        new_status: RequestStatus,
        changed_by: int | None = None,
        comment: str | None = None,
    ) -> RequestStatusHistory:
        item = RequestStatusHistory(
            request_id=request_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            comment=comment,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_stale_new(self, hours: int = 24) -> list[Request]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self.session.execute(
            select(Request)
            .where(Request.status == RequestStatus.NEW)
            .where(Request.created_at < cutoff)
            .order_by(Request.created_at)
        )
        return list(result.scalars().all())
