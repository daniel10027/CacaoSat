from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin, utcnow
from app.models.enums import EudrStatus, RiskLevel

_enum = {"native_enum": False, "values_callable": lambda e: [m.value for m in e]}


class ComplianceScore(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "compliance_scores"

    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(sa.Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        sa.Enum(RiskLevel, length=10, **_enum), nullable=False
    )
    eudr_status: Mapped[EudrStatus] = mapped_column(
        sa.Enum(EudrStatus, length=16, **_enum), nullable=False
    )
    factors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    computed_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, default=utcnow
    )

    parcel: Mapped[Parcel] = relationship(back_populates="scores")  # noqa: F821
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="score")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ComplianceScore {self.score:.0f} {self.eudr_status}>"
