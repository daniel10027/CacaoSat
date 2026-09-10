"""Mock Digital Earth Africa — suivi de la dégradation des terres.

Affine l'analyse de risque, en particulier en zones frontalières.
"""

from __future__ import annotations

from shapely.geometry.base import BaseGeometry

from app.mocks.base import seeded_rng
from app.mocks.scenarios import Scenario

PROVIDER_VERSION = "dea-mock/1.0 (Digital Earth Africa land degradation, déterministe)"


def degradation_index(parcel_id: object, geom: BaseGeometry, scenario: Scenario) -> dict:
    rng = seeded_rng("dea", parcel_id)
    index = round(min(1.0, max(0.0, scenario.degradation_index + rng.normal(0, 0.03))), 4)
    # Tendance sur 3 ans (négatif = aggravation).
    trend = round(scenario.ndvi_trend * 12 + rng.normal(0, 0.002), 5)
    return {
        "degradation_index": index,
        "trend_per_year": trend,
        "class": "stable" if index < 0.3 else ("moderate" if index < 0.6 else "severe"),
    }


def describe() -> dict:
    return {"provider": "digital_earth_africa", "version": PROVIDER_VERSION, "mock": True}
