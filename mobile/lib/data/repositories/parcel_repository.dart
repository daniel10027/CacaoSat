import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import 'package:uuid/uuid.dart';

import '../../domain/geo.dart';
import '../local/database.dart';

class ParcelValidation {
  const ParcelValidation({required this.ok, this.errors = const [], this.warnings = const []});
  final bool ok;
  final List<String> errors;
  final List<String> warnings;
}

class ParcelRepository {
  ParcelRepository(this._dao, this._sync, this._ref);
  final ParcelDao _dao;
  final SyncDao _sync;
  final ReferenceDao _ref;
  final _uuid = const Uuid();

  Future<List<Parcel>> all() => _dao.all();
  Future<Parcel?> byId(String id) => _dao.byId(id);

  Future<ParcelValidation> validate(List<LatLng> ring) async {
    final errors = <String>[];
    final warnings = <String>[];
    if (ring.length < 3) errors.add('Au moins 3 sommets requis.');
    if (Geo.selfIntersects(ring)) errors.add('Le contour se recoupe.');
    if (!Geo.withinCotedIvoire(ring)) errors.add('Hors de la Côte d\'Ivoire.');
    final area = Geo.areaHa(ring);
    if (area < 0.05) errors.add('Surface trop petite (${area.toStringAsFixed(2)} ha).');
    if (area > 50) errors.add('Surface irréaliste (${area.toStringAsFixed(1)} ha).');

    final protectedRings = await _protectedRings();
    if (Geo.intersectsAnyProtected(ring, protectedRings)) {
      warnings.add('La parcelle recoupe une aire protégée / forêt classée.');
    }
    return ParcelValidation(ok: errors.isEmpty, errors: errors, warnings: warnings);
  }

  Future<Parcel> create({
    required String coopId,
    required String coopCode,
    required List<LatLng> ring,
    String? producerLocalId,
    int? plantingYear,
    String crop = 'cocoa',
    double? gpsAccuracyM,
    String collectionMethod = 'walk',
    String? note,
  }) async {
    final id = _uuid.v4();
    final now = DateTime.now();
    final seq = (await _dao.countAll()) + 1;
    final code = '$coopCode-${seq.toString().padLeft(4, '0')}';
    final geojson = Geo.toGeoJson(ring);
    final area = Geo.areaHa(ring);

    await _dao.upsert(ParcelsCompanion(
      id: Value(id),
      producerLocalId: Value(producerLocalId),
      coopId: Value(coopId),
      code: Value(code),
      geojson: Value(geojson),
      areaHa: Value(area),
      plantingYear: Value(plantingYear),
      crop: Value(crop),
      gpsAccuracyM: Value(gpsAccuracyM),
      collectionMethod: Value(collectionMethod),
      collectedAt: Value(now),
      note: Value(note),
      syncState: const Value('pending'),
      updatedAt: Value(now),
    ));

    await _sync.enqueue(SyncQueueCompanion(
      entity: const Value('parcel'),
      op: const Value('create'),
      localId: Value(id),
      payload: Value(jsonEncode({
        'client_id': id,
        'code': code,
        'geometry': jsonDecode(geojson),
        'producer_client_id': producerLocalId,
        'planting_year': plantingYear,
        'crop': crop,
        'gps_accuracy_m': gpsAccuracyM,
        'collection_method': collectionMethod,
        'collected_at': now.toUtc().toIso8601String(),
        'cooperative_id': coopId,
        'updated_at': now.toUtc().toIso8601String(),
      })),
      createdAt: Value(now),
    ));

    return (await _dao.byId(id))!;
  }

  Future<List<List<LatLng>>> _protectedRings() async {
    final raw = await _ref.get('bootstrap');
    if (raw == null) return const [];
    final fc = (jsonDecode(raw) as Map)['protected_areas'] as Map?;
    if (fc == null) return const [];
    final out = <List<LatLng>>[];
    for (final f in (fc['features'] as List)) {
      final geom = (f as Map)['geometry'] as Map;
      if (geom['type'] != 'Polygon') continue;
      final ring = (geom['coordinates'] as List).first as List;
      out.add(ring
          .map((c) => LatLng((c as List)[1] as double, c[0] as double))
          .toList());
    }
    return out;
  }
}
