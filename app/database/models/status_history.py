from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import RequestStatus


class RequestStatusHistory(Base):
    __tablename__ = "request_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_status: Mapped[RequestStatus | None] = mapped_column(
        Enum(RequestStatus, name="request_status", native_enum=True)
    )
    new_status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status", native_enum=True),
        nullable=False,
    )
    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("managers.id", ondelete="SET NULL")
    )
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    request: Mapped["Request"] = relationship(back_populates="status_history")
    manager: Mapped["Manager | None"] = relationship(back_populates="status_changes")
