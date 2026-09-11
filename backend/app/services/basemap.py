"""Fond de carte raster (tuiles Web Mercator) pour le PDF de conformité.

Le rapport doit rester générable sans réseau : toute défaillance — service
injoignable, tuile manquante, budget de temps dépassé, Pillow absent — se
traduit par un ``None`` et l'appelant retombe sur le rendu vectoriel seul.
Aucune exception ne remonte de ce module.

Les tuiles sont mises en cache sur disque : un même périmètre régénéré
plusieurs fois ne rappelle pas le fournisseur.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import logging
import math
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen

from flask import current_app

log = logging.getLogger(__name__)

TILE = 256
MAX_LAT = 85.05112878  # limite de la projection Web Mercator
_UA = "CacaoSat/1.0 (rapport de conformité EUDR)"


@dataclass(frozen=True)
class Basemap:
    """Image du fond de carte et repères permettant d'y caler les parcelles."""

    png: bytes
    width_px: int
    height_px: int
    zoom: int
    origin_x: float  # pixel global Web Mercator du bord gauche de l'image
    origin_y: float  # pixel global Web Mercator du bord haut de l'image
    attribution: str

    def project(self, lon: float, lat: float) -> tuple[float, float]:
        """Position (0..1) du point dans l'image, depuis le coin haut-gauche."""
        px, py = lonlat_to_pixel(lon, lat, self.zoom)
        return (px - self.origin_x) / self.width_px, (py - self.origin_y) / self.height_px

    def metres_per_pixel(self, lat: float) -> float:
        return 156543.03392 * math.cos(math.radians(lat)) / (2**self.zoom)


def lonlat_to_pixel(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    """Coordonnées pixel globales Web Mercator (origine : coin haut-gauche du monde)."""
    n = TILE * 2**zoom
    lat = max(min(lat, MAX_LAT), -MAX_LAT)
    sin = math.sin(math.radians(lat))
    x = (lon + 180.0) / 360.0 * n
    y = (0.5 - math.log((1 + sin) / (1 - sin)) / (4 * math.pi)) * n
    return x, y


def _pick_zoom(bbox: tuple[float, float, float, float], max_px: int, max_tiles: int) -> int | None:
    """Plus grand zoom dont l'emprise tient dans le budget pixels et tuiles."""
    west, south, east, north = bbox
    for zoom in range(18, 4, -1):
        x0, y0 = lonlat_to_pixel(west, north, zoom)
        x1, y1 = lonlat_to_pixel(east, south, zoom)
        if (x1 - x0) > max_px or (y1 - y0) > max_px:
            continue
        cols = int(x1 // TILE) - int(x0 // TILE) + 1
        rows = int(y1 // TILE) - int(y0 // TILE) + 1
        if cols * rows <= max_tiles:
            return zoom
    return None


def _cache_dir() -> Path | None:
    raw = current_app.config.get("REPORT_BASEMAP_CACHE_DIR") or ""
    base = Path(raw) if raw else Path(tempfile.gettempdir()) / "cacaosat-tiles"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return base


def _fetch_tile(url_tpl: str, zoom: int, x: int, y: int, timeout: float, cache: Path | None) -> bytes | None:
    path = None
    if cache is not None:
        key = hashlib.sha256(f"{url_tpl}|{zoom}|{x}|{y}".encode()).hexdigest()
        path = cache / f"{key}.tile"
        try:
            if path.is_file():
                return path.read_bytes()
        except OSError:
            path = None

    url = url_tpl.format(z=zoom, x=x, y=y)
    for attempt in (1, 2):  # une seule reprise : un aléa réseau ne doit pas coûter cher
        try:
            with urlopen(Request(url, headers={"User-Agent": _UA}), timeout=timeout) as resp:
                data = resp.read()
            break
        except Exception as exc:  # noqa: BLE001 — toute erreur est non fatale
            if attempt == 2:
                log.info("fond de carte : tuile %s/%s/%s indisponible (%s)", zoom, x, y, exc)
                return None
    if path is not None:
        with contextlib.suppress(OSError):
            path.write_bytes(data)
    return data


def _plan(
    bbox: tuple[float, float, float, float], max_px: int, max_tiles: int
) -> tuple[str, float, float, int] | None:
    """Préconditions : fond activé, source définie, emprise dans le budget."""
    cfg = current_app.config
    if not cfg.get("REPORT_BASEMAP_ENABLED", False):
        return None
    url_tpl = cfg.get("REPORT_BASEMAP_URL") or ""
    if not url_tpl:
        return None
    zoom = _pick_zoom(bbox, max_px, max_tiles)
    if zoom is None:
        log.info("fond de carte ignoré : emprise hors budget (%s)", bbox)
        return None
    return (
        url_tpl,
        float(cfg.get("REPORT_BASEMAP_TIMEOUT", 6)),
        float(cfg.get("REPORT_BASEMAP_BUDGET", 20)),
        zoom,
    )


def build(
    bbox: tuple[float, float, float, float], *, max_px: int = 1600, max_tiles: int = 48
) -> Basemap | None:
    """Assemble le fond de carte couvrant ``bbox`` (west, south, east, north).

    Retourne ``None`` dès que le fond ne peut pas être produit intégralement :
    un fond partiel induirait en erreur sur un document de conformité.
    """
    plan = _plan(bbox, max_px, max_tiles)
    if plan is None:
        return None
    url_tpl, timeout, budget, zoom = plan

    try:
        from PIL import Image
    except ImportError:  # pragma: no cover — Pillow est une dépendance déclarée
        log.warning("fond de carte ignoré : Pillow indisponible")
        return None

    started = time.monotonic()
    west, south, east, north = bbox
    x0, y0 = lonlat_to_pixel(west, north, zoom)
    x1, y1 = lonlat_to_pixel(east, south, zoom)
    tx0, ty0 = int(x0 // TILE), int(y0 // TILE)
    tx1, ty1 = int(x1 // TILE), int(y1 // TILE)
    coords = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]

    cache = _cache_dir()
    with ThreadPoolExecutor(max_workers=6) as pool:
        blobs = list(pool.map(lambda c: _fetch_tile(url_tpl, zoom, c[0], c[1], timeout, cache), coords))
    if any(b is None for b in blobs):
        return None
    if time.monotonic() - started > budget:
        log.info("fond de carte ignoré : budget de %.0fs dépassé", budget)
        return None

    try:
        canvas = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE))
        for (tx, ty), blob in zip(coords, blobs, strict=True):
            tile = Image.open(io.BytesIO(blob)).convert("RGB")
            if tile.size != (TILE, TILE):
                tile = tile.resize((TILE, TILE))
            canvas.paste(tile, ((tx - tx0) * TILE, (ty - ty0) * TILE))

        # Découpe sur des pixels entiers, et l'origine réelle est renvoyée telle
        # quelle : les parcelles se calent ainsi exactement sur l'image.
        left = math.floor(x0 - tx0 * TILE)
        top = math.floor(y0 - ty0 * TILE)
        right = math.ceil(x1 - tx0 * TILE)
        bottom = math.ceil(y1 - ty0 * TILE)
        img = canvas.crop((left, top, right, bottom))

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
    except Exception as exc:  # noqa: BLE001
        log.info("fond de carte ignoré : assemblage impossible (%s)", exc)
        return None

    return Basemap(
        png=buf.getvalue(),
        width_px=img.width,
        height_px=img.height,
        zoom=zoom,
        origin_x=tx0 * TILE + left,
        origin_y=ty0 * TILE + top,
        attribution=current_app.config.get("REPORT_BASEMAP_ATTRIBUTION", ""),
    )
