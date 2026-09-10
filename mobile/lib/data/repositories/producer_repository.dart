import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../local/database.dart';

class ProducerRepository {
  ProducerRepository(this._dao, this._sync);
  final ProducerDao _dao;
  final SyncDao _sync;
  final _uuid = const Uuid();

  Future<List<Producer>> all() => _dao.all();
  Future<Producer?> byId(String id) => _dao.byId(id);

  /// Crée un producteur localement + met en file de synchronisation.
  Future<Producer> create({
    required String coopId,
    required String fullName,
    String? nationalId,
    String gender = 'unknown',
    String? village,
    String? phone,
  }) async {
    final id = _uuid.v4();
    final now = DateTime.now();
    final row = ProducersCompanion(
      id: Value(id),
      coopId: Value(coopId),
      fullName: Value(fullName),
      nationalId: Value(nationalId),
      gender: Value(gender),
      village: Value(village),
      phone: Value(phone),
      registeredAt: Value(now),
      dirty: const Value(true),
      deleted: const Value(false),
      updatedAt: Value(now),
    );
    await _dao.upsert(row);
    await _sync.enqueue(SyncQueueCompanion(
      entity: const Value('producer'),
      op: const Value('create'),
      localId: Value(id),
      payload: Value(jsonEncode({
        'client_id': id,
        'full_name': fullName,
        'national_id': nationalId,
        'gender': gender,
        'village': village,
        'phone': phone,
        'cooperative_id': coopId,
        'updated_at': now.toUtc().toIso8601String(),
      })),
      createdAt: Value(now),
    ));
    return (await _dao.byId(id))!;
  }
}
