from __future__ import annotations

import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin, utcnow


class ComplianceReport(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "compliance_reports"

    cooperative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("cooperatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    period_start: Mapped[date | None] = mapped_column(sa.Date)
    period_end: Mapped[date | None] = mapped_column(sa.Date)
    parcel_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    pdf_key: Mapped[str | None] = mapped_column(sa.String(300))
    geojson_key: Mapped[str | None] = mapped_column(sa.String(300))
    content_hash: Mapped[str | None] = mapped_column(sa.String(64))
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    generated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, default=utcnow
    )

    cooperative: Mapped[Cooperative] = relationship()  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ComplianceReport {self.title}>"
