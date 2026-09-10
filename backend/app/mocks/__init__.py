"""Mocks déterministes des services externes.

Les implémentations concrètes (Sentinel-2, Hansen/GFW, Digital Earth Africa,
aires protégées, e-mail, SMS, stockage objet) arrivent au Lot 2 et au Lot 3.
Chaque mock expose un `provider_version` et respecte une interface remplaçable
par une vraie intégration.
"""

DEFAULT_SEED = 42
