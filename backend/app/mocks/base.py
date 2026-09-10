"""Socle commun des mocks : RNG déterministe + interfaces remplaçables."""

from __future__ import annotations

import hashlib
from typing import Protocol

import numpy as np

from app.mocks import DEFAULT_SEED


def seeded_rng(*keys: object, seed: int = DEFAULT_SEED) -> np.random.Generator:
    """Générateur NumPy déterministe pour une combinaison de clés (ex. parcel.id)."""
    material = "|".join(str(k) for k in keys) + f"|{seed}"
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


class SatelliteProvider(Protocol):
    """Contrat qu'une vraie intégration (Copernicus, GFW, DEA) devra respecter."""

    provider_version: str

    def describe(self) -> dict: ...
