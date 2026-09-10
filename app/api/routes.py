from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentActor, get_db, require_admin, require_staff
from app.api.schemas import (
    HistoryRead,
    ManagerRead,
    RequestCreate,
    RequestRead,
    StatusUpdate,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.core.config import settings
from app.core.exceptions import InvalidStatusTransitionError, NotFoundError
from app.core.security import create_access_token
from app.database.models.enums import RequestStatus, UserRole
from app.repositories.manager_repository import ManagerRepository
from app.repositories.user_repository import UserRepository
from app.services.request_service import RequestService

router = APIRouter(prefix="/api/v1")


@router.post("/auth/dev-token", response_model=TokenResponse)
async def dev_token(
    manager_id: int,
    session: AsyncSession = Depends(get_db),
):
    if settings.environment == "production":
        raise HTTPException(404, "Not available in production")

    manager = await ManagerRepository(session).get_by_id(manager_id)
    if not manager or not manager.is_active:
        raise HTTPException(404, "Manager not found")
    return TokenResponse(
        access_token=create_access_token(str(manager.id), manager.role.value)
    )


@router.post("/users", response_model=UserRead)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_db)):
    user = await UserRepository(session).get_or_create(**data.model_dump())
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/requests", response_model=RequestRead, status_code=201)
async def create_request(
    data: RequestCreate,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await RequestService(session).create_request(**data.model_dump())
    except Exception:
        await session.rollback()
        raise


@router.get("/requests", response_model=list[RequestRead])
async def list_requests(
    status: RequestStatus | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: CurrentActor = Depends(require_staff),
    session: AsyncSession = Depends(get_db),
):
    return await RequestService(session).list_requests(status, limit, offset)


@router.get("/requests/{request_id}", response_model=RequestRead)
async def get_request(
    request_id: int,
    _: CurrentActor = Depends(require_staff),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await RequestService(session).get_request(request_id)
    except NotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.patch("/requests/{request_id}/status", response_model=RequestRead)
async def update_status(
    request_id: int,
    data: StatusUpdate,
    actor: CurrentActor = Depends(require_staff),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await RequestService(session).change_status(
            request_id=request_id,
            new_status=data.status,
            changed_by=int(actor.subject),
            comment=data.comment,
        )
    except NotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/requests/{request_id}/history", response_model=list[HistoryRead])
async def request_history(
    request_id: int,
    _: CurrentActor = Depends(require_staff),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await RequestService(session).get_history(request_id)
    except NotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/statistics")
async def statistics(
    _: CurrentActor = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    requests = await RequestService(session).list_requests(limit=500)
    result = {status.value: 0 for status in RequestStatus}
    for item in requests:
        result[item.status.value] += 1
    return {"total": len(requests), "by_status": result}


@router.get("/managers", response_model=list[ManagerRead])
async def managers(
    _: CurrentActor = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    return await ManagerRepository(session).get_active()
