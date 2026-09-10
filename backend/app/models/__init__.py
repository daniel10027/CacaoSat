"""Modèles SQLAlchemy — importés ici pour peupler `db.metadata`."""

from app.models.alert import Alert
from app.models.analysis_run import AnalysisRun
from app.models.audit_log import AuditLog
from app.models.compliance_report import ComplianceReport
from app.models.compliance_score import ComplianceScore
from app.models.cooperative import Cooperative
from app.models.parcel import Parcel
from app.models.producer import Producer
from app.models.sync_batch import SyncBatch
from app.models.user import User

__all__ = [
    "Alert",
    "AnalysisRun",
    "AuditLog",
    "ComplianceReport",
    "ComplianceScore",
    "Cooperative",
    "Parcel",
    "Producer",
    "SyncBatch",
    "User",
]
