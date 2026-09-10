from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AccessDeniedError, InvalidStatusTransitionError, NotFoundError
from app.database.models.enums import RequestStatus
from app.repositories.request_repository import RequestRepository


ALLOWED_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.NEW: {
        RequestStatus.IN_PROGRESS,
        RequestStatus.CONTACTED,
        RequestStatus.REJECTED,
    },
    RequestStatus.IN_PROGRESS: {
        RequestStatus.CONTACTED,
        RequestStatus.CALCULATING,
        RequestStatus.REJECTED,
    },
    RequestStatus.CONTACTED: {
        RequestStatus.CALCULATING,
        RequestStatus.REJECTED,
    },
    RequestStatus.CALCULATING: {
        RequestStatus.APPROVED,
        RequestStatus.REJECTED,
    },
    RequestStatus.APPROVED: {
        RequestStatus.COMPLETED,
        RequestStatus.REJECTED,
    },
    RequestStatus.REJECTED: set(),
    RequestStatus.COMPLETED: set(),
}


class RequestService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RequestRepository(session)

    async def create_request(self, **data):
        request = await self.repo.create(**data)
        await self.repo.add_history(
            request_id=request.id,
            old_status=None,
            new_status=RequestStatus.NEW,
            comment="Request created",
        )
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_request(self, request_id: int):
        request = await self.repo.get_by_id(request_id)
        if not request:
            raise NotFoundError("Request not found")
        return request

    async def get_user_requests(self, user_id: int):
        return await self.repo.get_by_user(user_id)

    async def list_requests(self, status=None, limit=100, offset=0):
        return await self.repo.list_all(status, limit, offset)

    async def change_status(
        self,
        request_id: int,
        new_status: RequestStatus,
        changed_by: int | None = None,
        comment: str | None = None,
    ):
        request = await self.get_request(request_id)
        old_status = request.status

        if old_status == new_status:
            return request

        if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
            raise InvalidStatusTransitionError(
                f"{old_status} -> {new_status} is not allowed"
            )

        request.status = new_status
        await self.repo.add_history(
            request_id=request.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            comment=comment,
        )
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_history(self, request_id: int):
        await self.get_request(request_id)
        return await self.repo.get_history(request_id)

    async def ensure_owner(self, request_id: int, user_id: int):
        request = await self.get_request(request_id)
        if request.user_id != user_id:
            raise AccessDeniedError("You do not have access to this request")
        return request
