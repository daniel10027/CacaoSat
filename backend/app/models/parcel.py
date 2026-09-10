from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import CollectionMethod, ParcelSource, ParcelStatus

_enum = {"native_enum": False, "values_callable": lambda e: [m.value for m in e]}


class Parcel(UUIDMixin, TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "parcels"

    code: Mapped[str] = mapped_column(sa.String(32), nullable=False, unique=True, index=True)
    producer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("producers.id", ondelete="SET NULL"),
        index=True,
    )
    cooperative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("cooperatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    geometry = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True), nullable=False
    )
    centroid = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True
    )

    area_ha: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0.0)
    planting_year: Mapped[int | None] = mapped_column(sa.SmallInteger)
    crop: Mapped[str] = mapped_column(sa.String(40), nullable=False, default="cocoa")
    gps_accuracy_m: Mapped[float | None] = mapped_column(sa.Float)
    collection_method: Mapped[CollectionMethod] = mapped_column(
        sa.Enum(CollectionMethod, length=16, **_enum),
        nullable=False,
        default=CollectionMethod.MANUAL,
    )
    collected_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    collected_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    source: Mapped[ParcelSource] = mapped_column(
        sa.Enum(ParcelSource, length=12, **_enum), nullable=False, default=ParcelSource.WEB
    )
    status: Mapped[ParcelStatus] = mapped_column(
        sa.Enum(ParcelStatus, length=12, **_enum), nullable=False, default=ParcelStatus.ACTIVE
    )

    producer: Mapped[Producer | None] = relationship(back_populates="parcels")  # noqa: F821
    cooperative: Mapped[Cooperative] = relationship(back_populates="parcels")  # noqa: F821
    analyses: Mapped[list[AnalysisRun]] = relationship(  # noqa: F821
        back_populates="parcel",
        cascade="all, delete-orphan",
        order_by="AnalysisRun.created_at.desc()",
    )
    scores: Mapped[list[ComplianceScore]] = relationship(  # noqa: F821
        back_populates="parcel",
        cascade="all, delete-orphan",
        order_by="ComplianceScore.computed_at.desc()",
    )
    alerts: Mapped[list[Alert]] = relationship(  # noqa: F821
        back_populates="parcel", cascade="all, delete-orphan"
    )

    @property
    def latest_score(self) -> ComplianceScore | None:  # noqa: F821
        return self.scores[0] if self.scores else None

    @property
    def latest_analysis(self) -> AnalysisRun | None:  # noqa: F821
        return self.analyses[0] if self.analyses else None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Parcel {self.code}>"
