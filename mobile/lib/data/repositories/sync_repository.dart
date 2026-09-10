import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../local/database.dart';
import '../remote/api_client.dart';

class SyncOutcome {
  const SyncOutcome({
    required this.batchId,
    required this.accepted,
    required this.rejected,
    required this.errors,
  });
  final String batchId;
  final int accepted;
  final int rejected;
  final List<Map<String, dynamic>> errors;
}

class SyncRepository {
  SyncRepository(this._api, this._sync, this._producers, this._parcels);
  final ApiClient _api;
  final SyncDao _sync;
  final ProducerDao _producers;
  final ParcelDao _parcels;
  final _uuid = const Uuid();

  Future<int> pendingCount() async {
    final items = await _sync.pending();
    return items.length;
  }

  /// Envoie tous les éléments en attente en un batch idempotent.
  Future<SyncOutcome> pushAll({String deviceId = 'mobile'}) async {
    final queued = await _sync.pending();
    if (queued.isEmpty) {
      return const SyncOutcome(batchId: '', accepted: 0, rejected: 0, errors: []);
    }

    // Producteurs avant parcelles (dépendances).
    queued.sort((a, b) => (a.entity == 'producer' ? 0 : 1)
        .compareTo(b.entity == 'producer' ? 0 : 1));

    final clientBatchId = _uuid.v4();
    final items = queued
        .map((q) => {
              'op': q.op,
              'entity': q.entity,
              'client_id': q.localId,
              'data': jsonDecode(q.payload),
            })
        .toList();

    final res = await _api.post<Map<String, dynamic>>('/sync/batch', body: {
      'device_id': deviceId,
      'client_batch_id': clientBatchId,
      'items': items,
    });
    final data = res.data!;
    final idMap = (data['id_map'] as Map).cast<String, String>();
    final errors = (data['errors'] as List? ?? const [])
        .map((e) => (e as Map).cast<String, dynamic>())
        .toList();
    final rejectedIds = errors.map((e) => e['client_id']).toSet();

    for (final q in queued) {
      final serverId = idMap[q.localId];
      if (serverId != null) {
        if (q.entity == 'producer') {
          await _producers.markSynced(q.localId, serverId);
        } else {
          await _parcels.markSynced(q.localId, serverId);
        }
        await _sync.remove(q.id);
      } else if (rejectedIds.contains(q.localId)) {
        await _sync.bumpAttempt(q.id, 'rejeté par le serveur');
      }
    }

    await _sync.logOutbox(OutboxLogCompanion(
      batchId: Value(data['batch_id'] as String?),
      sentAt: Value(DateTime.now()),
      accepted: Value((data['accepted'] as num?)?.toInt() ?? 0),
      rejected: Value((data['rejected'] as num?)?.toInt() ?? 0),
      response: Value(jsonEncode(data)),
    ));

    // Récupère les scores calculés côté serveur.
    if (data['batch_id'] != null) {
      await _pullStatuses(data['batch_id'] as String);
    }

    return SyncOutcome(
      batchId: data['batch_id'] as String? ?? '',
      accepted: (data['accepted'] as num?)?.toInt() ?? 0,
      rejected: (data['rejected'] as num?)?.toInt() ?? 0,
      errors: errors,
    );
  }

  Future<void> _pullStatuses(String batchId) async {
    try {
      final res =
          await _api.get<Map<String, dynamic>>('/sync/status/$batchId');
      for (final p in (res.data!['parcels'] as List? ?? const [])) {
        final m = p as Map<String, dynamic>;
        if (m['analyzed'] == true && m['score'] != null) {
          await _parcels.setScore(
            m['parcel_id'] as String,
            (m['score'] as num).toDouble(),
            m['eudr_status'] as String? ?? 'unassessed',
          );
        }
      }
    } catch (_) {
      // silencieux : les scores seront rattrapés au prochain bootstrap
    }
  }

  Future<List<OutboxLogData>> outbox() => _sync.outbox();
}
