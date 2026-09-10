import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

part 'database.g.dart';

// --- Tables -----------------------------------------------------------------

class Producers extends Table {
  TextColumn get id => text()(); // UUID local
  TextColumn get serverId => text().nullable()();
  TextColumn get coopId => text()();
  TextColumn get fullName => text()();
  TextColumn get nationalId => text().nullable()();
  TextColumn get gender => text().withDefault(const Constant('unknown'))();
  TextColumn get village => text().nullable()();
  TextColumn get phone => text().nullable()();
  DateTimeColumn get registeredAt => dateTime().nullable()();
  BoolColumn get dirty => boolean().withDefault(const Constant(true))();
  BoolColumn get deleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class Parcels extends Table {
  TextColumn get id => text()(); // UUID local
  TextColumn get serverId => text().nullable()();
  TextColumn get producerLocalId => text().nullable()();
  TextColumn get coopId => text()();
  TextColumn get code => text()();
  TextColumn get geojson => text()(); // GeoJSON Polygon (EPSG:4326)
  RealColumn get areaHa => real().withDefault(const Constant(0))();
  IntColumn get plantingYear => integer().nullable()();
  TextColumn get crop => text().withDefault(const Constant('cocoa'))();
  RealColumn get gpsAccuracyM => real().nullable()();
  TextColumn get collectionMethod => text().withDefault(const Constant('walk'))();
  DateTimeColumn get collectedAt => dateTime()();
  TextColumn get note => text().nullable()();
  // pending | synced | analyzed
  TextColumn get syncState => text().withDefault(const Constant('pending'))();
  RealColumn get score => real().nullable()();
  TextColumn get eudrStatus => text().nullable()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class ReferenceData extends Table {
  TextColumn get key => text()();
  TextColumn get json => text()();
  DateTimeColumn get fetchedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {key};
}

class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get entity => text()(); // producer | parcel
  TextColumn get op => text()(); // create | update
  TextColumn get localId => text()();
  TextColumn get payload => text()(); // JSON
  DateTimeColumn get createdAt => dateTime()();
  IntColumn get attempts => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
}

class OutboxLog extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get batchId => text().nullable()();
  DateTimeColumn get sentAt => dateTime()();
  IntColumn get accepted => integer().withDefault(const Constant(0))();
  IntColumn get rejected => integer().withDefault(const Constant(0))();
  TextColumn get response => text().nullable()();
}

// --- Base -----------------------------------------------------------------

@DriftDatabase(
  tables: [Producers, Parcels, ReferenceData, SyncQueue, OutboxLog],
  daos: [ProducerDao, ParcelDao, SyncDao, ReferenceDao],
)
class AppDatabase extends _$AppDatabase {
  AppDatabase([QueryExecutor? executor]) : super(executor ?? _open());

  AppDatabase.forTesting(super.executor);

  @override
  int get schemaVersion => 1;

  static QueryExecutor _open() {
    return LazyDatabase(() async {
      final dir = await getApplicationDocumentsDirectory();
      final file = File(p.join(dir.path, 'cacaosat.sqlite'));
      return NativeDatabase.createInBackground(file);
    });
  }
}

// --- DAOs -----------------------------------------------------------------

@DriftAccessor(tables: [Producers])
class ProducerDao extends DatabaseAccessor<AppDatabase> with _$ProducerDaoMixin {
  ProducerDao(super.db);

  Future<List<Producer>> all() =>
      (select(producers)..where((t) => t.deleted.equals(false))).get();

  Stream<List<Producer>> watchAll() =>
      (select(producers)..where((t) => t.deleted.equals(false))).watch();

  Future<Producer?> byId(String id) =>
      (select(producers)..where((t) => t.id.equals(id))).getSingleOrNull();

  Future<void> upsert(ProducersCompanion row) =>
      into(producers).insertOnConflictUpdate(row);

  Future<int> countDirty() async {
    final q = selectOnly(producers)
      ..addColumns([producers.id.count()])
      ..where(producers.dirty.equals(true));
    final row = await q.getSingle();
    return row.read(producers.id.count()) ?? 0;
  }

  Future<void> markSynced(String id, String serverId) =>
      (update(producers)..where((t) => t.id.equals(id))).write(
        ProducersCompanion(serverId: Value(serverId), dirty: const Value(false)),
      );
}

@DriftAccessor(tables: [Parcels])
class ParcelDao extends DatabaseAccessor<AppDatabase> with _$ParcelDaoMixin {
  ParcelDao(super.db);

  Future<List<Parcel>> all() =>
      (select(parcels)..orderBy([(t) => OrderingTerm.desc(t.collectedAt)])).get();

  Stream<List<Parcel>> watchAll() =>
      (select(parcels)..orderBy([(t) => OrderingTerm.desc(t.collectedAt)])).watch();

  Future<Parcel?> byId(String id) =>
      (select(parcels)..where((t) => t.id.equals(id))).getSingleOrNull();

  Future<void> upsert(ParcelsCompanion row) =>
      into(parcels).insertOnConflictUpdate(row);

  Future<int> countPending() async {
    final q = selectOnly(parcels)
      ..addColumns([parcels.id.count()])
      ..where(parcels.syncState.equals('pending'));
    final row = await q.getSingle();
    return row.read(parcels.id.count()) ?? 0;
  }

  Future<void> markSynced(String id, String serverId) =>
      (update(parcels)..where((t) => t.id.equals(id))).write(
        ParcelsCompanion(serverId: Value(serverId), syncState: const Value('synced')),
      );

  Future<void> setScore(String serverId, double score, String status) =>
      (update(parcels)..where((t) => t.serverId.equals(serverId))).write(
        ParcelsCompanion(
          score: Value(score),
          eudrStatus: Value(status),
          syncState: const Value('analyzed'),
        ),
      );

  Future<int> countAll() async {
    final q = selectOnly(parcels)..addColumns([parcels.id.count()]);
    return (await q.getSingle()).read(parcels.id.count()) ?? 0;
  }
}

@DriftAccessor(tables: [SyncQueue, OutboxLog])
class SyncDao extends DatabaseAccessor<AppDatabase> with _$SyncDaoMixin {
  SyncDao(super.db);

  Future<int> enqueue(SyncQueueCompanion row) => into(syncQueue).insert(row);

  Future<List<SyncQueueData>> pending() => (select(syncQueue)
        ..orderBy([(t) => OrderingTerm.asc(t.id)]))
      .get();

  Stream<int> watchPendingCount() {
    final q = selectOnly(syncQueue)..addColumns([syncQueue.id.count()]);
    return q.watchSingle().map((r) => r.read(syncQueue.id.count()) ?? 0);
  }

  Future<void> remove(int id) =>
      (delete(syncQueue)..where((t) => t.id.equals(id))).go();

  Future<void> bumpAttempt(int id, String error) async {
    final row = await (select(syncQueue)..where((t) => t.id.equals(id)))
        .getSingleOrNull();
    if (row == null) return;
    await (update(syncQueue)..where((t) => t.id.equals(id))).write(
      SyncQueueCompanion(attempts: Value(row.attempts + 1), lastError: Value(error)),
    );
  }

  Future<void> logOutbox(OutboxLogCompanion row) => into(outboxLog).insert(row);

  Future<List<OutboxLogData>> outbox() => (select(outboxLog)
        ..orderBy([(t) => OrderingTerm.desc(t.sentAt)])
        ..limit(30))
      .get();
}

@DriftAccessor(tables: [ReferenceData])
class ReferenceDao extends DatabaseAccessor<AppDatabase> with _$ReferenceDaoMixin {
  ReferenceDao(super.db);

  Future<void> put(String key, String json) => into(referenceData).insertOnConflictUpdate(
        ReferenceDataCompanion(
          key: Value(key),
          json: Value(json),
          fetchedAt: Value(DateTime.now()),
        ),
      );

  Future<String?> get(String key) async {
    final row = await (select(referenceData)..where((t) => t.key.equals(key)))
        .getSingleOrNull();
    return row?.json;
  }

  Future<DateTime?> fetchedAt(String key) async {
    final row = await (select(referenceData)..where((t) => t.key.equals(key)))
        .getSingleOrNull();
    return row?.fetchedAt;
  }
}
