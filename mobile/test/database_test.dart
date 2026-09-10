import 'package:cacaosat/data/local/database.dart';
import 'package:cacaosat/data/repositories/parcel_repository.dart';
import 'package:cacaosat/data/repositories/producer_repository.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late AppDatabase db;

  setUp(() => db = AppDatabase.forTesting(NativeDatabase.memory()));
  tearDown(() => db.close());

  test('création producteur -> file de sync', () async {
    final repo = ProducerRepository(db.producerDao, db.syncDao);
    final p = await repo.create(
      coopId: 'coop-1',
      fullName: 'Kouamé Yao',
      nationalId: 'CI123',
      village: 'Zéaglo',
    );
    expect(p.dirty, isTrue);
    expect((await db.producerDao.all()).length, 1);
    expect((await db.syncDao.pending()).length, 1);
    expect((await db.producerDao.countDirty()), 1);
  });

  test('création parcelle : surface calculée + file de sync', () async {
    final repo = ParcelRepository(db.parcelDao, db.syncDao, db.referenceDao);
    const lon = -7.492, lat = 6.544, d = 0.0006;
    final parcel = await repo.create(
      coopId: 'coop-1',
      coopCode: 'COOP',
      ring: [
        const LatLng(lat - d, lon - d),
        const LatLng(lat - d, lon + d),
        const LatLng(lat + d, lon + d),
        const LatLng(lat + d, lon - d),
      ],
    );
    expect(parcel.code, 'COOP-0001');
    expect(parcel.areaHa, greaterThan(0));
    expect(parcel.syncState, 'pending');
    expect((await db.parcelDao.countPending()), 1);
    final queued = await db.syncDao.pending();
    expect(queued.single.entity, 'parcel');
  });

  test('validate rejette une surface trop petite', () async {
    final repo = ParcelRepository(db.parcelDao, db.syncDao, db.referenceDao);
    const lon = -7.492, lat = 6.544, d = 0.00002;
    final v = await repo.validate([
      const LatLng(lat - d, lon - d),
      const LatLng(lat - d, lon + d),
      const LatLng(lat + d, lon),
    ]);
    expect(v.ok, isFalse);
  });

  test('markSynced renseigne le serverId', () async {
    final repo = ProducerRepository(db.producerDao, db.syncDao);
    final p = await repo.create(coopId: 'c', fullName: 'Test');
    await db.producerDao.markSynced(p.id, 'server-uuid');
    final updated = await db.producerDao.byId(p.id);
    expect(updated!.serverId, 'server-uuid');
    expect(updated.dirty, isFalse);
  });
}
