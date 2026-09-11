"""Fond de carte du PDF : projection, choix du zoom et garde-fous hors ligne.

Aucun test ne sollicite le réseau — `TestConfig` désactive le fond, et les
fonctions de projection sont pures.
"""

from __future__ import annotations

import math

import pytest

from app.services import basemap
from app.services.report import _framed_bbox, _merc_y, _merc_y_inv


def test_pixel_origin_is_world_centre():
    # Au zoom 0 le monde tient dans une tuile : (0,0) tombe en son centre.
    x, y = basemap.lonlat_to_pixel(0.0, 0.0, 0)
    assert x == pytest.approx(basemap.TILE / 2)
    assert y == pytest.approx(basemap.TILE / 2)


def test_pixel_grows_east_and_south():
    west = basemap.lonlat_to_pixel(-7.5, 6.5, 14)
    east = basemap.lonlat_to_pixel(-7.4, 6.5, 14)
    south = basemap.lonlat_to_pixel(-7.5, 6.4, 14)
    assert east[0] > west[0], "vers l'est, x doit croître"
    assert south[1] > west[1], "vers le sud, y doit croître (origine en haut)"


def test_pixel_scale_doubles_with_zoom():
    a = basemap.lonlat_to_pixel(-7.5, 6.5, 12)
    b = basemap.lonlat_to_pixel(-7.5, 6.5, 13)
    assert b[0] == pytest.approx(a[0] * 2)
    assert b[1] == pytest.approx(a[1] * 2)


def test_latitude_is_clamped_to_mercator_limit():
    # Sans bornage, la formule diverge au pôle.
    top = basemap.lonlat_to_pixel(0.0, 89.9, 5)
    edge = basemap.lonlat_to_pixel(0.0, basemap.MAX_LAT, 5)
    assert top[1] == pytest.approx(edge[1])
    assert math.isfinite(top[1])


def test_mercator_roundtrip():
    for lat in (-40.0, -6.5, 0.0, 6.5, 51.2):
        assert _merc_y_inv(_merc_y(lat)) == pytest.approx(lat, abs=1e-9)


def test_pick_zoom_prefers_the_largest_that_fits():
    bbox = (-7.52, 6.48, -7.46, 6.54)  # ~6,6 km de côté
    zoom = basemap._pick_zoom(bbox, max_px=1600, max_tiles=48)
    assert zoom is not None
    x0, y0 = basemap.lonlat_to_pixel(bbox[0], bbox[3], zoom)
    x1, y1 = basemap.lonlat_to_pixel(bbox[2], bbox[1], zoom)
    assert (x1 - x0) <= 1600 and (y1 - y0) <= 1600
    # Le zoom suivant doit, lui, dépasser le budget : sinon il aurait été retenu.
    nx0, ny0 = basemap.lonlat_to_pixel(bbox[0], bbox[3], zoom + 1)
    nx1, ny1 = basemap.lonlat_to_pixel(bbox[2], bbox[1], zoom + 1)
    assert (nx1 - nx0) > 1600 or (ny1 - ny0) > 1600


def test_pick_zoom_gives_up_on_a_world_extent():
    assert basemap._pick_zoom((-180.0, -80.0, 180.0, 80.0), max_px=1600, max_tiles=48) is None


def test_build_returns_none_when_disabled(app):
    # TestConfig coupe le fond : la génération d'un rapport ne doit jamais
    # déclencher d'appel sortant dans la suite.
    with app.app_context():
        assert basemap.build((-7.52, 6.48, -7.46, 6.54)) is None


def test_build_returns_none_without_url(app):
    with app.app_context():
        app.config["REPORT_BASEMAP_ENABLED"] = True
        app.config["REPORT_BASEMAP_URL"] = ""
        try:
            assert basemap.build((-7.52, 6.48, -7.46, 6.54)) is None
        finally:
            app.config["REPORT_BASEMAP_ENABLED"] = False


def test_basemap_project_places_corners_at_the_edges():
    bbox = (-7.52, 6.48, -7.46, 6.54)
    zoom = 14
    x0, y0 = basemap.lonlat_to_pixel(bbox[0], bbox[3], zoom)
    x1, y1 = basemap.lonlat_to_pixel(bbox[2], bbox[1], zoom)
    bm = basemap.Basemap(
        png=b"", width_px=int(x1 - x0), height_px=int(y1 - y0), zoom=zoom,
        origin_x=x0, origin_y=y0, attribution="",
    )
    assert bm.project(bbox[0], bbox[3]) == pytest.approx((0.0, 0.0), abs=1e-6)
    assert bm.project(bbox[2], bbox[1]) == pytest.approx((1.0, 1.0), abs=1e-3)


def test_metres_per_pixel_shrinks_with_zoom():
    bm = basemap.Basemap(b"", 100, 100, 14, 0.0, 0.0, "")
    deeper = basemap.Basemap(b"", 100, 100, 15, 0.0, 0.0, "")
    assert deeper.metres_per_pixel(6.5) == pytest.approx(bm.metres_per_pixel(6.5) / 2)


class _Box:
    """Substitut minimal de géométrie : seul ``bounds`` est utilisé."""

    def __init__(self, minx, miny, maxx, maxy):
        self.bounds = (minx, miny, maxx, maxy)


def test_framed_bbox_matches_the_frame_ratio():
    # C'est ce qui corrige le cadre à moitié vide : l'emprise doit épouser le
    # ratio du dessin, en espace Mercator.
    geoms = [_Box(-7.50, 6.50, -7.49, 6.51)]
    aspect = 170 / 120
    west, south, east, north = _framed_bbox(geoms, aspect)
    w = (east - west) / 360
    h = _merc_y(south) - _merc_y(north)
    assert w / h == pytest.approx(aspect, rel=1e-6)


def test_framed_bbox_centres_the_parcels():
    geoms = [_Box(-7.50, 6.50, -7.49, 6.51)]
    west, south, east, north = _framed_bbox(geoms, 170 / 120)
    assert (west + east) / 2 == pytest.approx((-7.50 + -7.49) / 2, abs=1e-9)
    centre_y = (_merc_y(north) + _merc_y(south)) / 2
    assert _merc_y_inv(centre_y) == pytest.approx((6.50 + 6.51) / 2, abs=1e-6)


def test_framed_bbox_survives_a_single_point():
    # Une coopérative réduite à une parcelle ponctuelle ne doit pas produire
    # une emprise nulle, qui ferait diverger le calcul de zoom.
    geoms = [_Box(-7.50, 6.50, -7.50, 6.50)]
    west, south, east, north = _framed_bbox(geoms, 170 / 120)
    assert east > west and north > south
