from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin, utcnow
from app.models.enums import SyncStatus

_enum = {"native_enum": False, "values_callable": lambda e: [m.value for m in e]}


class SyncBatch(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "sync_batches"
    __table_args__ = (
        sa.UniqueConstraint("device_id", "client_batch_id", name="uq_sync_batches_device_client"),
    )

    device_id: Mapped[str] = mapped_column(sa.String(120), nullable=False, index=True)
    client_batch_id: Mapped[str | None] = mapped_column(sa.String(64))
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    received_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, default=utcnow
    )
    item_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    accepted: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    rejected: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    errors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    id_map: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[SyncStatus] = mapped_column(
        sa.Enum(SyncStatus, length=10, **_enum), nullable=False, default=SyncStatus.PENDING
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SyncBatch {self.device_id} {self.status}>"
