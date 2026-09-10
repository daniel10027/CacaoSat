"""Énumérations métier (stockées en VARCHAR + CHECK, non natives)."""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    AGENT = "agent"
    MANAGER = "manager"
    EXPORTER = "exporter"
    REGULATOR = "regulator"
    ADMIN = "admin"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class CollectionMethod(StrEnum):
    WALK = "walk"
    VERTICES = "vertices"
    MANUAL = "manual"
    IMPORT = "import"


class ParcelSource(StrEnum):
    MOBILE = "mobile"
    WEB = "web"
    IMPORT = "import"


class ParcelStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EudrStatus(StrEnum):
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    NON_COMPLIANT = "non_compliant"


class AlertType(StrEnum):
    NEW_DEFORESTATION = "new_deforestation"
    PROTECTED_ENCROACHMENT = "protected_encroachment"
    DATA_GAP = "data_gap"


class AlertSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SyncStatus(StrEnum):
    PENDING = "pending"
    PARTIAL = "partial"
    DONE = "done"
    FAILED = "failed"


def values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]
