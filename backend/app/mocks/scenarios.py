"""Attribution déterministe d'un scénario de conformité à chaque parcelle.

Trois scénarios pilotent l'ensemble des mocks pour une démo reproductible :

- ``compliant``   : aucune perte de couvert depuis 2020, hors aire protégée.
- ``at_risk``     : perte diffuse limitée (~2-4 % de la surface), NDVI en léger déclin.
- ``deforested``  : coupe nette après 2020 et/ou fort recouvrement d'aire protégée.

Le scénario est dérivé de l'identifiant de la parcelle (hash) — sauf override
explicite via ``SCENARIO_OVERRIDES`` (par code de parcelle), utile pour scénariser
la démo.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.mocks.base import seeded_rng

SCENARIOS = ("compliant", "at_risk", "deforested")

# Pondération de tirage : la majorité des parcelles sont conformes.
_WEIGHTS = (0.62, 0.26, 0.12)

# Forcer un scénario pour certaines parcelles (démo).
SCENARIO_OVERRIDES: dict[str, str] = {}


@dataclass(frozen=True)
class Scenario:
    name: str
    # fraction de la surface ayant perdu son couvert après le 31/12/2020
    loss_fraction: float
    # mois (offset depuis start) de l'événement de coupe, ou None
    loss_month: int | None
    # amplitude de la chute de NDVI lors de l'événement (0-1)
    ndvi_drop: float
    # tendance de fond du NDVI par mois (négatif = dégradation)
    ndvi_trend: float
    # indice de dégradation des terres (DEA), 0 (sain) .. 1 (dégradé)
    degradation_index: float
    # fraction de la parcelle recouvrant une aire protégée (approx. attendue)
    protected_hint: float


def resolve(parcel_id: object, parcel_code: str | None = None) -> Scenario:
    if parcel_code and parcel_code in SCENARIO_OVERRIDES:
        name = SCENARIO_OVERRIDES[parcel_code]
    else:
        rng = seeded_rng("scenario", parcel_id)
        name = str(rng.choice(SCENARIOS, p=_WEIGHTS))

    rng = seeded_rng("scenario-params", parcel_id)
    if name == "compliant":
        return Scenario(
            name=name,
            loss_fraction=0.0,
            loss_month=None,
            ndvi_drop=0.0,
            ndvi_trend=float(rng.uniform(-0.001, 0.0015)),
            degradation_index=float(rng.uniform(0.02, 0.18)),
            protected_hint=0.0,
        )
    if name == "at_risk":
        return Scenario(
            name=name,
            loss_fraction=float(rng.uniform(0.015, 0.045)),
            loss_month=int(rng.integers(10, 30)),
            ndvi_drop=float(rng.uniform(0.05, 0.12)),
            ndvi_trend=float(rng.uniform(-0.004, -0.0015)),
            degradation_index=float(rng.uniform(0.28, 0.5)),
            protected_hint=float(rng.uniform(0.0, 0.08)),
        )
    # deforested
    return Scenario(
        name=name,
        loss_fraction=float(rng.uniform(0.08, 0.35)),
        loss_month=int(rng.integers(6, 30)),
        ndvi_drop=float(rng.uniform(0.25, 0.5)),
        ndvi_trend=float(rng.uniform(-0.006, -0.003)),
        degradation_index=float(rng.uniform(0.55, 0.85)),
        protected_hint=float(rng.uniform(0.1, 0.6)),
    )
