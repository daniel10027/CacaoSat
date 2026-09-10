import pytest
from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon

from app.errors import ApiError
from app.geo import polygon_area_ha, polygon_centroid, to_wkt_element, validate_polygon
from app.models import Cooperative, Parcel


def _parcel_polygon() -> Polygon:
    # ~1 ha près de Guiglo (Cavally)
    lon, lat = -7.492, 6.544
    d = 0.00045
    return Polygon(
        [(lon - d, lat - d), (lon + d, lat - d), (lon + d, lat + d), (lon - d, lat + d), (lon - d, lat - d)]
    )


def test_area_ha_is_plausible():
    area = polygon_area_ha(_parcel_polygon())
    assert 0.5 < area < 2.0


def test_validate_polygon_rejects_out_of_country():
    paris = Polygon([(2.2, 48.8), (2.4, 48.8), (2.4, 48.9), (2.2, 48.9), (2.2, 48.8)])
    with pytest.raises(ApiError):
        validate_polygon(paris)


def test_validate_polygon_rejects_self_intersection():
    bowtie = Polygon([(-7.49, 6.54), (-7.48, 6.55), (-7.48, 6.54), (-7.49, 6.55), (-7.49, 6.54)])
    with pytest.raises(ApiError):
        validate_polygon(bowtie)


def test_parcel_geometry_roundtrip(db):
    coop = Cooperative(code="COOP-GEO", name="Coop Géo")
    db.session.add(coop)
    db.session.flush()

    poly = _parcel_polygon()
    cx, cy = polygon_centroid(poly)
    parcel = Parcel(
        code="COOP-GEO-0001",
        cooperative=coop,
        geometry=to_wkt_element(poly),
        area_ha=polygon_area_ha(poly),
    )
    db.session.add(parcel)
    db.session.commit()
    db.session.expire_all()

    fetched = db.session.get(Parcel, parcel.id)
    shape = to_shape(fetched.geometry)
    assert shape.geom_type == "Polygon"
    assert shape.equals_exact(poly, tolerance=1e-6)
    assert round(shape.centroid.x, 4) == round(cx, 4)


def test_spatial_index_exists(db):
    rows = db.session.execute(
        db.text("SELECT indexname FROM pg_indexes WHERE tablename = 'parcels'")
    ).scalars().all()
    assert any("geometry" in name for name in rows)
