"""Mock du fournisseur d'imagerie Sentinel-2 (Copernicus).

Produit une série temporelle mensuelle de NDVI pour une géométrie donnée,
de façon déterministe. Peut simuler une chute nette de NDVI (coupe forestière)
à une date choisie par le scénario.
"""

from __future__ import annotations

from datetime import date

import numpy as np
from shapely.geometry.base import BaseGeometry

from app.mocks.base import seeded_rng
from app.mocks.scenarios import Scenario

PROVIDER_VERSION = "sentinel2-mock/1.0 (Copernicus S2 L2A NDVI, 10m, déterministe)"

# Fenêtre d'observation par défaut : 2020-01 -> aujourd'hui (borné à ~5 ans).
DEFAULT_START = date(2020, 1, 1)


def _month_index(d: date, start: date) -> int:
    return (d.year - start.year) * 12 + (d.month - start.month)


def ndvi_series(
    parcel_id: object,
    geom: BaseGeometry,
    scenario: Scenario,
    start: date = DEFAULT_START,
    end: date | None = None,
) -> list[dict]:
    end = end or date.today()
    n_months = max(6, _month_index(end, start) + 1)
    rng = seeded_rng("ndvi", parcel_id)

    # Niveau de base propre à la parcelle (couvert cacao dense ~0.75-0.85).
    base = float(rng.uniform(0.72, 0.86))
    noise = rng.normal(0.0, 0.02, size=n_months)

    series: list[dict] = []
    dropped = 0.0
    for m in range(n_months):
        y = start.year + (start.month - 1 + m) // 12
        mo = (start.month - 1 + m) % 12 + 1
        # Saisonnalité (saison sèche déc-fév => NDVI plus bas).
        seasonal = 0.05 * np.sin(2 * np.pi * (m + 1) / 12.0 - 1.2)
        trend = scenario.ndvi_trend * m

        if scenario.loss_month is not None and m >= scenario.loss_month:
            # Chute permanente après l'événement, proportionnelle à la fraction perdue.
            dropped = scenario.ndvi_drop * min(1.0, 0.4 + scenario.loss_fraction * 3)

        value = base + seasonal + trend + noise[m] - dropped
        series.append(
            {
                "date": date(y, mo, 15).isoformat(),
                "ndvi": round(float(np.clip(value, 0.05, 0.95)), 4),
            }
        )
    return series


def describe() -> dict:
    return {"provider": "sentinel2", "version": PROVIDER_VERSION, "mock": True}
