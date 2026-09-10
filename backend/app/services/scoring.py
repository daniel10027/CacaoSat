"""Moteur de scoring de conformité EUDR — logique pondérée et explicable.

Barème (100 points) :

| Facteur                                   | Poids |
|-------------------------------------------|------:|
| Déforestation post-2020 sur la parcelle   |    45 |
| Recouvrement d'une aire protégée          |    20 |
| Tendance NDVI / dégradation des terres    |    15 |
| Complétude de la donnée                    |    10 |
| Qualité du relevé GPS + fraîcheur          |    10 |

`risk_level` : score ≥ 80 → low · 50-79 → medium · < 50 → high
`eudr_status` : compliant (low & 0 déforestation & 0 recouvrement) · at_risk · non_compliant
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.analysis_run import AnalysisRun
from app.models.compliance_score import ComplianceScore
from app.models.enums import EudrStatus, RiskLevel
from app.models.parcel import Parcel

W_DEFOREST = 45
W_PROTECTED = 20
W_TREND = 15
W_COMPLETENESS = 10
W_GPS = 10

# Une perte > 5 % de la surface annule le facteur déforestation.
LOSS_RATIO_ZERO = 0.05


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _months_since(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    now = datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return (now - dt).days / 30.44


def compute_score(run: AnalysisRun, parcel: Parcel, context: dict | None = None) -> ComplianceScore:
    context = context or {}
    area_ha = max(float(parcel.area_ha or 0.0), 0.01)
    degradation = context.get("degradation") or {}
    degradation_index = float(degradation.get("degradation_index", 0.25))
    ndvi_breaks = context.get("ndvi_breaks") or []

    factors: list[dict] = []

    # 1. Déforestation post-2020 ------------------------------------------------
    loss_ratio = float(run.forest_loss_ha or 0.0) / area_ha
    if run.forest_loss_ha == 0:
        pts_def = float(W_DEFOREST)
        expl = "Aucune perte de couvert détectée depuis le 31/12/2020."
    else:
        pts_def = round(W_DEFOREST * _clamp(1 - loss_ratio / LOSS_RATIO_ZERO), 2)
        expl = (
            f"{run.forest_loss_ha:.3f} ha perdus depuis 2020 "
            f"({loss_ratio * 100:.1f} % de la parcelle)."
        )
    factors.append(
        {
            "key": "deforestation_post_2020",
            "label": "Déforestation post-2020",
            "weight": W_DEFOREST,
            "raw_value": round(run.forest_loss_ha or 0.0, 4),
            "points": pts_def,
            "explanation": expl,
        }
    )

    # 2. Recouvrement d'aire protégée ----------------------------------------------
    overlap_ratio = float(run.protected_area_overlap_ha or 0.0) / area_ha
    pts_prot = round(W_PROTECTED * _clamp(1 - overlap_ratio), 2)
    factors.append(
        {
            "key": "protected_area_overlap",
            "label": "Recouvrement d'aire protégée / forêt classée",
            "weight": W_PROTECTED,
            "raw_value": round(run.protected_area_overlap_ha or 0.0, 4),
            "points": pts_prot,
            "explanation": (
                "Hors de toute aire protégée."
                if overlap_ratio == 0
                else f"{overlap_ratio * 100:.1f} % de la parcelle en aire protégée."
            ),
        }
    )

    # 3. Tendance NDVI / dégradation (DEA) --------------------------------------
    pts_trend = round(W_TREND * _clamp(1 - degradation_index / 0.6), 2)
    if any(b.get("ndvi_drop", 0) >= 0.15 for b in ndvi_breaks):
        pts_trend = min(pts_trend, 3.0)
    factors.append(
        {
            "key": "ndvi_degradation_trend",
            "label": "Tendance NDVI / dégradation des terres",
            "weight": W_TREND,
            "raw_value": round(degradation_index, 4),
            "points": pts_trend,
            "explanation": (
                f"Indice de dégradation {degradation_index:.2f} "
                f"({degradation.get('class', 'n/a')})."
            ),
        }
    )

    # 4. Complétude de la donnée ---------------------------------------------------
    pts_comp = float(W_COMPLETENESS)
    missing: list[str] = []
    if parcel.producer_id is None:
        pts_comp -= 4
        missing.append("producteur non rattaché")
    elif not (parcel.producer and parcel.producer.national_id):
        pts_comp -= 3
        missing.append("pièce d'identité du producteur absente")
    if parcel.geometry is None:
        pts_comp -= 3
        missing.append("géométrie manquante")
    pts_comp = round(max(0.0, pts_comp), 2)
    factors.append(
        {
            "key": "data_completeness",
            "label": "Complétude de la donnée",
            "weight": W_COMPLETENESS,
            "raw_value": "complète" if not missing else ", ".join(missing),
            "points": pts_comp,
            "explanation": "Dossier complet." if not missing else "Manque : " + ", ".join(missing),
        }
    )

    # 5. Qualité du relevé GPS + fraîcheur ------------------------------------------
    acc = parcel.gps_accuracy_m
    if acc is None:
        pts_acc = 3.0
    else:
        pts_acc = 6.0 * _clamp((20.0 - float(acc)) / 15.0)
    months = _months_since(parcel.collected_at)
    if months is None:
        pts_fresh = 2.0
    else:
        pts_fresh = 4.0 * _clamp((36.0 - months) / 24.0)
    pts_gps = round(pts_acc + pts_fresh, 2)
    factors.append(
        {
            "key": "gps_quality_freshness",
            "label": "Qualité du relevé GPS et fraîcheur",
            "weight": W_GPS,
            "raw_value": {
                "gps_accuracy_m": acc,
                "age_months": round(months, 1) if months is not None else None,
            },
            "points": pts_gps,
            "explanation": (
                f"Précision {acc} m, "
                f"relevé il y a {months:.0f} mois." if months is not None
                else f"Précision {acc} m, date de relevé inconnue."
            ),
        }
    )

    score = round(min(100.0, max(0.0, sum(f["points"] for f in factors))), 1)

    if score >= 80:
        risk = RiskLevel.LOW
    elif score >= 50:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.HIGH

    if (
        risk is RiskLevel.HIGH
        or (run.deforestation_detected and loss_ratio > LOSS_RATIO_ZERO)
        or overlap_ratio > 0.25
    ):
        status = EudrStatus.NON_COMPLIANT
    elif (
        risk is RiskLevel.LOW
        and run.forest_loss_ha == 0
        and run.protected_area_overlap_ha == 0
        and not run.deforestation_detected
    ):
        status = EudrStatus.COMPLIANT
    else:
        status = EudrStatus.AT_RISK

    return ComplianceScore(
        parcel_id=parcel.id,
        analysis_run_id=run.id,
        score=score,
        risk_level=risk,
        eudr_status=status,
        factors=factors,
    )
