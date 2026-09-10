import 'dart:convert';

import 'package:drift/drift.dart';

import '../local/database.dart';
import '../remote/api_client.dart';

/// Récupère et stocke les données de référence pour le mode hors-ligne.
class ReferenceRepository {
  ReferenceRepository(this._api, this._ref, this._producers, this._parcels);

  final ApiClient _api;
  final ReferenceDao _ref;
  final ProducerDao _producers;
  final ParcelDao _parcels;

  Future<DateTime?> get lastBootstrap => _ref.fetchedAt('bootstrap');

  Future<Map<String, dynamic>?> cachedBootstrap() async {
    final raw = await _ref.get('bootstrap');
    return raw == null ? null : jsonDecode(raw) as Map<String, dynamic>;
  }

  Future<List<List<List<double>>>> protectedRings() async {
    final b = await cachedBootstrap();
    final fc = b?['protected_areas'] as Map<String, dynamic>?;
    if (fc == null) return const [];
    final rings = <List<List<double>>>[];
    for (final f in (fc['features'] as List)) {
      final geom = (f as Map)['geometry'] as Map;
      if (geom['type'] == 'Polygon') {
        final ring = (geom['coordinates'] as List).first as List;
        rings.add(ring
            .map<List<double>>(
                (c) => [(c as List)[0] as double, c[1] as double])
            .toList());
      }
    }
    return rings;
  }

  /// Télécharge le bootstrap et hydrate la base locale.
  Future<void> refresh() async {
    final res = await _api.get<Map<String, dynamic>>('/sync/bootstrap');
    final data = res.data!;
    await _ref.put('bootstrap', jsonEncode(data));

    final coop = data['cooperative'] as Map<String, dynamic>?;
    final coopId = coop?['id'] as String? ?? '';

    for (final p in (data['producers'] as List? ?? const [])) {
      final m = p as Map<String, dynamic>;
      await _producers.upsert(ProducersCompanion(
        id: Value(m['id'] as String),
        serverId: Value(m['id'] as String),
        coopId: Value(m['cooperative_id'] as String? ?? coopId),
        fullName: Value(m['full_name'] as String),
        nationalId: Value(m['national_id'] as String?),
        gender: Value(m['gender'] as String? ?? 'unknown'),
        village: Value(m['village'] as String?),
        phone: Value(m['phone'] as String?),
        dirty: const Value(false),
        deleted: const Value(false),
        updatedAt: Value(DateTime.now()),
      ));
    }

    for (final p in (data['parcels'] as List? ?? const [])) {
      final m = p as Map<String, dynamic>;
      await _parcels.upsert(ParcelsCompanion(
        id: Value(m['id'] as String),
        serverId: Value(m['id'] as String),
        coopId: Value(m['cooperative_id'] as String? ?? coopId),
        code: Value(m['code'] as String),
        geojson: Value(jsonEncode(m['geometry'])),
        areaHa: Value((m['area_ha'] as num?)?.toDouble() ?? 0),
        collectionMethod: Value(m['collection_method'] as String? ?? 'walk'),
        collectedAt: Value(
          DateTime.tryParse(m['collected_at'] as String? ?? '') ?? DateTime.now(),
        ),
        score: Value((m['latest_score']?['score'] as num?)?.toDouble()),
        eudrStatus: Value(m['latest_score']?['eudr_status'] as String?),
        syncState: Value(m['latest_score'] == null ? 'synced' : 'analyzed'),
        updatedAt: Value(DateTime.now()),
      ));
    }
  }
}
