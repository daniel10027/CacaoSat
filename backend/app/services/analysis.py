"""Moteur d'analyse : croise la parcelle avec les couches satellites (mockées)
et produit un ``AnalysisRun`` persistant."""

from __future__ import annotations

from datetime import date

from geoalchemy2.shape import to_shape

from app.extensions import db
from app.mocks import digital_earth_africa as dea
from app.mocks import gfw_hansen, protected_areas, scenarios, sentinel2
from app.models.analysis_run import AnalysisRun
from app.models.parcel import Parcel

EUDR_CUTOFF = date(2020, 12, 31)
NDVI_BREAK_THRESHOLD = 0.12
NDVI_DEFOREST_THRESHOLD = 0.15


def _rolling_mean(values: list[float], window: int) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        chunk = values[lo : i + 1]
        out.append(sum(chunk) / len(chunk))
    return out


def detect_ndvi_breaks(ndvi_series: list[dict], window: int = 3) -> list[dict]:
    """Détecte les ruptures baissières de NDVI (candidats coupe forestière)."""
    if len(ndvi_series) < 2 * window:
        return []
    values = [p["ndvi"] for p in ndvi_series]
    dates = [p["date"] for p in ndvi_series]
    smooth = _rolling_mean(values, window)

    breaks: list[dict] = []
    for split in range(window, len(values) - window):
        before = sum(smooth[split - window : split]) / window
        after = sum(smooth[split : split + window]) / window
        drop = round(before - after, 4)
        if drop >= NDVI_BREAK_THRESHOLD:
            breaks.append(
                {
                    "date": dates[split],
                    "ndvi_before": round(before, 4),
                    "ndvi_after": round(after, 4),
                    "ndvi_drop": drop,
                    "source": "sentinel2_ndvi",
                }
            )

    # Fusionne les ruptures consécutives, garde la plus marquée par épisode.
    merged: list[dict] = []
    for b in breaks:
        if merged and _months_between(merged[-1]["date"], b["date"]) <= window:
            if b["ndvi_drop"] > merged[-1]["ndvi_drop"]:
                merged[-1] = b
        else:
            merged.append(b)
    return merged


def _months_between(iso_a: str, iso_b: str) -> int:
    ya, ma, _ = iso_a.split("-")
    yb, mb, _ = iso_b.split("-")
    return abs((int(yb) - int(ya)) * 12 + (int(mb) - int(ma)))


def _confidence(forest_loss_ha: float, area_ha: float, ndvi_breaks: list[dict], dea_class: str,
                overlap_ha: float) -> float:
    loss_signal = forest_loss_ha > max(0.02 * area_ha, 0.03)
    ndvi_signal = any(b["ndvi_drop"] >= NDVI_DEFOREST_THRESHOLD for b in ndvi_breaks)
    score = 0.5
    if loss_signal == ndvi_signal:
        score += 0.2
    if (dea_class == "severe") == loss_signal:
        score += 0.15
    if (overlap_ha > 0) or (not loss_signal and not ndvi_signal):
        score += 0.15
    return round(min(1.0, score), 3)


def run_analysis(parcel: Parcel) -> tuple[AnalysisRun, dict]:
    """Retourne l'``AnalysisRun`` (non persisté) et un contexte pour le scoring."""
    geom = to_shape(parcel.geometry)
    area_ha = float(parcel.area_ha or 0.0)
    scenario = scenarios.resolve(parcel.id, parcel.code)

    ndvi = sentinel2.ndvi_series(parcel.id, geom, scenario)
    forest = gfw_hansen.forest_stats(parcel.id, geom, scenario)
    degradation = dea.degradation_index(parcel.id, geom, scenario)
    overlap_ha = protected_areas.overlap_ha(geom)

    ndvi_breaks = [
        b for b in detect_ndvi_breaks(ndvi) if b["date"] > EUDR_CUTOFF.isoformat()
    ]

    forest_loss_ha = float(forest["forest_loss_ha_post_2020"])
    loss_events = list(forest["loss_events"]) + ndvi_breaks

    deforestation_detected = bool(
        forest_loss_ha > max(0.03 * area_ha, 0.05)
        or any(b["ndvi_drop"] >= NDVI_DEFOREST_THRESHOLD for b in ndvi_breaks)
    )

    run = AnalysisRun(
        parcel_id=parcel.id,
        provider_versions={
            "sentinel2": sentinel2.PROVIDER_VERSION,
            "gfw_hansen": gfw_hansen.PROVIDER_VERSION,
            "digital_earth_africa": dea.PROVIDER_VERSION,
            "protected_areas": protected_areas.PROVIDER_VERSION,
            "scenario": scenario.name,
        },
        forest_cover_2020_pct=forest["forest_cover_2020_pct"],
        forest_cover_current_pct=forest["forest_cover_current_pct"],
        forest_loss_ha=forest_loss_ha,
        loss_events=loss_events,
        ndvi_series=ndvi,
        protected_area_overlap_ha=overlap_ha,
        deforestation_detected=deforestation_detected,
        confidence=_confidence(
            forest_loss_ha, area_ha, ndvi_breaks, degradation["class"], overlap_ha
        ),
    )
    context = {
        "degradation": degradation,
        "scenario": scenario.name,
        "ndvi_breaks": ndvi_breaks,
        "pre_2020_loss_ha": forest["pre_2020_loss_ha"],
    }
    return run, context


def analyze_parcel(parcel_id) -> tuple[AnalysisRun, ComplianceScore]:  # noqa: F821
    from app.services.scoring import compute_score

    parcel = db.session.get(Parcel, parcel_id)
    if parcel is None:
        raise ValueError(f"Parcelle introuvable : {parcel_id}")

    run, context = run_analysis(parcel)
    db.session.add(run)
    db.session.flush()

    score = compute_score(run, parcel, context)
    db.session.add(score)
    db.session.commit()
    return run, score


def analyze_many(parcel_ids: list) -> dict:
    ok, failed = 0, []
    for pid in parcel_ids:
        try:
            analyze_parcel(pid)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            failed.append({"parcel_id": str(pid), "error": str(exc)})
    return {"analyzed": ok, "failed": failed, "total": len(parcel_ids)}
