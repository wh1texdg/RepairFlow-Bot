from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.database.models.enums import RequestStatus, UserRole


class RequestCreate(BaseModel):
    user_id: int
    object_type: str = Field(min_length=2, max_length=100)
    repair_type: str = Field(min_length=2, max_length=100)
    area: Decimal = Field(gt=0, le=10000)
    city: str = Field(min_length=2, max_length=255)
    address: str = Field(min_length=2, max_length=500)
    budget: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    desired_start_date: date
    description: str | None = Field(default=None, max_length=5000)

    @field_validator("desired_start_date")
    @classmethod
    def date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("desired_start_date cannot be in the past")
        return value


class StatusUpdate(BaseModel):
    status: RequestStatus
    comment: str | None = Field(default=None, max_length=2000)


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=10, max_length=32)


class UserRead(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class RequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    object_type: str
    repair_type: str
    area: Decimal
    city: str
    address: str
    budget: Decimal
    desired_start_date: date
    description: str | None
    status: RequestStatus
    created_at: datetime
    updated_at: datetime


class HistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    old_status: RequestStatus | None
    new_status: RequestStatus
    changed_by: int | None
    comment: str | None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ManagerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    name: str
    role: UserRole
    is_active: bool
