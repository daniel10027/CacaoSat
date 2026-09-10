from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin


class AnalysisRun(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "analysis_runs"

    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_versions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    forest_cover_2020_pct: Mapped[float | None] = mapped_column(sa.Float)
    forest_cover_current_pct: Mapped[float | None] = mapped_column(sa.Float)
    forest_loss_ha: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0.0)
    loss_events: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    ndvi_series: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    protected_area_overlap_ha: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0.0)
    deforestation_detected: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    confidence: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0.0)

    parcel: Mapped[Parcel] = relationship(back_populates="analyses")  # noqa: F821
    score: Mapped[ComplianceScore | None] = relationship(  # noqa: F821
        back_populates="analysis_run", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AnalysisRun parcel={self.parcel_id} loss={self.forest_loss_ha}ha>"
