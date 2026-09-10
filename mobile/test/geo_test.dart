import 'package:cacaosat/domain/geo.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';

void main() {
  group('Geo.areaHa', () {
    test('carré ~1 ha près de Guiglo', () {
      const lon = -7.492, lat = 6.544;
      const d = 0.00045; // ~50 m de demi-côté
      final ring = [
        const LatLng(lat - d, lon - d),
        const LatLng(lat - d, lon + d),
        const LatLng(lat + d, lon + d),
        const LatLng(lat + d, lon - d),
      ];
      final area = Geo.areaHa(ring);
      expect(area, greaterThan(0.5));
      expect(area, lessThan(2.0));
    });

    test('moins de 3 points -> 0', () {
      expect(Geo.areaHa([const LatLng(6, -7), const LatLng(6.1, -7)]), 0);
    });
  });

  group('validité géométrique', () {
    test('auto-intersection (nœud papillon) détectée', () {
      final bowtie = [
        const LatLng(6.54, -7.49),
        const LatLng(6.55, -7.48),
        const LatLng(6.54, -7.48),
        const LatLng(6.55, -7.49),
      ];
      expect(Geo.selfIntersects(bowtie), isTrue);
    });

    test('carré simple : pas d\'auto-intersection', () {
      final square = [
        const LatLng(6.54, -7.49),
        const LatLng(6.54, -7.48),
        const LatLng(6.55, -7.48),
        const LatLng(6.55, -7.49),
      ];
      expect(Geo.selfIntersects(square), isFalse);
    });

    test('emprise Côte d\'Ivoire', () {
      expect(
        Geo.withinCotedIvoire([const LatLng(6.5, -7.5)]),
        isTrue,
      );
      expect(
        Geo.withinCotedIvoire([const LatLng(48.8, 2.3)]),
        isFalse,
      );
    });
  });

  group('point dans polygone / aire protégée', () {
    final area = [
      const LatLng(6.514, -7.492),
      const LatLng(6.514, -7.450),
      const LatLng(6.545, -7.450),
      const LatLng(6.545, -7.492),
    ];

    test('point intérieur', () {
      expect(Geo.pointInPolygon(const LatLng(6.53, -7.47), area), isTrue);
    });

    test('recoupement d\'aire protégée', () {
      final parcel = [
        const LatLng(6.52, -7.47),
        const LatLng(6.52, -7.46),
        const LatLng(6.53, -7.46),
        const LatLng(6.53, -7.47),
      ];
      expect(Geo.intersectsAnyProtected(parcel, [area]), isTrue);
      final far = [
        const LatLng(6.90, -7.30),
        const LatLng(6.90, -7.29),
        const LatLng(6.91, -7.29),
      ];
      expect(Geo.intersectsAnyProtected(far, [area]), isFalse);
    });
  });

  group('GeoJSON round-trip', () {
    test('toGeoJson puis fromGeoJson conserve le contour', () {
      final ring = [
        const LatLng(6.544, -7.492),
        const LatLng(6.544, -7.491),
        const LatLng(6.545, -7.491),
        const LatLng(6.545, -7.492),
      ];
      final gj = Geo.toGeoJson(ring);
      final back = Geo.fromGeoJson(gj);
      expect(back.length, ring.length + 1); // anneau fermé
      expect(back.first.latitude, closeTo(ring.first.latitude, 1e-6));
    });
  });
}
