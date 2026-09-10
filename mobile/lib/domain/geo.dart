import 'dart:convert';
import 'dart:math' as math;

import 'package:latlong2/latlong.dart';

/// Utilitaires géométriques pour la capture de parcelles (100 % local).
class Geo {
  const Geo._();

  static const double earthRadiusM = 6378137.0;

  /// Emprise approximative de la Côte d'Ivoire (lon/lat).
  static const double ciMinLon = -8.75;
  static const double ciMinLat = 4.20;
  static const double ciMaxLon = -2.40;
  static const double ciMaxLat = 10.85;

  /// Surface géodésique d'un polygone en hectares (formule de l'aire sphérique).
  static double areaHa(List<LatLng> ring) {
    if (ring.length < 3) return 0;
    final pts = _closed(ring);
    double total = 0;
    for (var i = 0; i < pts.length - 1; i++) {
      final p1 = pts[i];
      final p2 = pts[i + 1];
      total += _rad(p2.longitude - p1.longitude) *
          (2 + math.sin(_rad(p1.latitude)) + math.sin(_rad(p2.latitude)));
    }
    final area = (total * earthRadiusM * earthRadiusM / 2.0).abs();
    return area / 10000.0;
  }

  static double perimeterM(List<LatLng> ring) {
    if (ring.length < 2) return 0;
    final pts = _closed(ring);
    const d = Distance();
    double total = 0;
    for (var i = 0; i < pts.length - 1; i++) {
      total += d.as(LengthUnit.Meter, pts[i], pts[i + 1]);
    }
    return total;
  }

  static LatLng centroid(List<LatLng> ring) {
    double x = 0, y = 0;
    for (final p in ring) {
      x += p.latitude;
      y += p.longitude;
    }
    return LatLng(x / ring.length, y / ring.length);
  }

  /// Le polygone est-il auto-intersectant ? (segments non adjacents qui se croisent)
  static bool selfIntersects(List<LatLng> ring) {
    final pts = _closed(ring);
    final n = pts.length - 1;
    if (n < 4) return false;
    for (var i = 0; i < n; i++) {
      for (var j = i + 1; j < n; j++) {
        if (j == i || (j + 1) % n == i || (i + 1) % n == j) continue;
        if (_segmentsCross(pts[i], pts[i + 1], pts[j], pts[j + 1])) return true;
      }
    }
    return false;
  }

  static bool withinCotedIvoire(List<LatLng> ring) {
    for (final p in ring) {
      if (p.longitude < ciMinLon ||
          p.longitude > ciMaxLon ||
          p.latitude < ciMinLat ||
          p.latitude > ciMaxLat) {
        return false;
      }
    }
    return true;
  }

  static bool pointInPolygon(LatLng point, List<LatLng> polygon) {
    var inside = false;
    final n = polygon.length;
    for (var i = 0, j = n - 1; i < n; j = i++) {
      final xi = polygon[i].longitude, yi = polygon[i].latitude;
      final xj = polygon[j].longitude, yj = polygon[j].latitude;
      final intersect = ((yi > point.latitude) != (yj > point.latitude)) &&
          (point.longitude < (xj - xi) * (point.latitude - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }

  /// Un des sommets du polygone tombe-t-il dans l'une des aires protégées ?
  static bool intersectsAnyProtected(
    List<LatLng> ring,
    List<List<LatLng>> protectedRings,
  ) {
    for (final area in protectedRings) {
      for (final v in ring) {
        if (pointInPolygon(v, area)) return true;
      }
      for (final v in area) {
        if (pointInPolygon(v, ring)) return true;
      }
    }
    return false;
  }

  /// GeoJSON Polygon (EPSG:4326) — anneau fermé, ordre lon/lat.
  static String toGeoJson(List<LatLng> ring) {
    final coords = _closed(ring)
        .map((p) => [
              double.parse(p.longitude.toStringAsFixed(7)),
              double.parse(p.latitude.toStringAsFixed(7)),
            ])
        .toList();
    return jsonEncode({
      'type': 'Polygon',
      'coordinates': [coords],
    });
  }

  static List<LatLng> fromGeoJson(String geojson) {
    final map = jsonDecode(geojson) as Map<String, dynamic>;
    final coords = (map['coordinates'] as List).first as List;
    return coords
        .map((c) => LatLng((c as List)[1] as double, c[0] as double))
        .toList();
  }

  // --- privé ---
  static List<LatLng> _closed(List<LatLng> ring) {
    if (ring.isEmpty) return ring;
    if (ring.first == ring.last) return ring;
    return [...ring, ring.first];
  }

  static double _rad(double deg) => deg * math.pi / 180.0;

  static bool _segmentsCross(LatLng a, LatLng b, LatLng c, LatLng d) {
    double cross(LatLng o, LatLng p, LatLng q) =>
        (p.longitude - o.longitude) * (q.latitude - o.latitude) -
        (p.latitude - o.latitude) * (q.longitude - o.longitude);
    final d1 = cross(c, d, a);
    final d2 = cross(c, d, b);
    final d3 = cross(a, b, c);
    final d4 = cross(a, b, d);
    return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
  }
}
