"""Mock Hansen / Global Forest Watch — couvert forestier & perte annuelle.

Retourne, pour une parcelle, le couvert arboré de référence, le couvert à fin 2020
(baseline EUDR) et l'historique de perte annuelle échantillonné sur une grille
déterministe dans le polygone.
"""

from __future__ import annotations

import numpy as np
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry

from app.geo import polygon_area_ha
from app.mocks.base import seeded_rng
from app.mocks.scenarios import Scenario

PROVIDER_VERSION = "gfw-hansen-mock/1.0 (Hansen v1.11 GFC tree cover + lossyear, déterministe)"

EUDR_CUTOFF_YEAR = 2020
_GRID = 12  # 12x12 points d'échantillonnage par parcelle


def _sample_points(geom: BaseGeometry, rng: np.random.Generator) -> list[Point]:
    minx, miny, maxx, maxy = geom.bounds
    pts: list[Point] = []
    xs = np.linspace(minx, maxx, _GRID)
    ys = np.linspace(miny, maxy, _GRID)
    for x in xs:
        for y in ys:
            p = Point(x + rng.normal(0, (maxx - minx) / (4 * _GRID)),
                      y + rng.normal(0, (maxy - miny) / (4 * _GRID)))
            if geom.covers(p):
                pts.append(p)
    return pts or [geom.centroid]


def forest_stats(parcel_id: object, geom: BaseGeometry, scenario: Scenario) -> dict:
    rng = seeded_rng("hansen", parcel_id)
    area_ha = polygon_area_ha(geom)
    points = _sample_points(geom, rng)
    n = len(points)
    cell_ha = area_ha / n if n else 0.0

    tree_cover_2000 = float(np.clip(rng.normal(88, 5), 60, 99))

    # Répartit la perte du scénario sur des années >= 2021.
    lost_cells = int(round(scenario.loss_fraction * n))
    loss_by_year: dict[int, float] = {}
    loss_events: list[dict] = []
    if lost_cells > 0:
        base_year = 2021
        if scenario.loss_month is not None:
            base_year = 2020 + max(1, scenario.loss_month // 12 + 1)
        years = rng.integers(base_year, min(base_year + 3, 2026) + 1, size=lost_cells)
        for yr in years:
            loss_by_year[int(yr)] = round(loss_by_year.get(int(yr), 0.0) + cell_ha, 4)
        for yr, ha in sorted(loss_by_year.items()):
            loss_events.append({"year": yr, "area_ha": round(ha, 4)})

    # ~1 % de perte "historique" avant 2020 (pré-baseline, non pénalisée).
    pre_2020_loss_ha = round(area_ha * float(rng.uniform(0.0, 0.02)), 4)
    forest_loss_ha_post_2020 = round(sum(loss_by_year.values()), 4)

    forest_cover_2020_pct = round(
        float(np.clip(tree_cover_2000 - (pre_2020_loss_ha / area_ha * 100 if area_ha else 0), 40, 99)),
        2,
    )
    forest_cover_current_pct = round(
        float(
            np.clip(
                forest_cover_2020_pct
                - (forest_loss_ha_post_2020 / area_ha * 100 if area_ha else 0),
                0,
                99,
            )
        ),
        2,
    )

    return {
        "tree_cover_2000_pct": round(tree_cover_2000, 2),
        "forest_cover_2020_pct": forest_cover_2020_pct,
        "forest_cover_current_pct": forest_cover_current_pct,
        "pre_2020_loss_ha": pre_2020_loss_ha,
        "forest_loss_ha_post_2020": forest_loss_ha_post_2020,
        "loss_events": loss_events,
        "sampled_points": n,
    }


def describe() -> dict:
    return {"provider": "gfw_hansen", "version": PROVIDER_VERSION, "mock": True}
