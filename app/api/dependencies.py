from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.models.enums import UserRole
from app.core.dependencies import session_dependency


@dataclass
class CurrentActor:
    subject: str
    role: UserRole


async def get_current_actor(
    authorization: str | None = Header(default=None),
) -> CurrentActor:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
        role = UserRole(payload["role"])
        return CurrentActor(subject=str(payload["sub"]), role=role)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


def require_staff(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
    if actor.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return actor


def require_admin(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
    if actor.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return actor


async def get_db(session: AsyncSession = Depends(session_dependency)) -> AsyncSession:
    return session
