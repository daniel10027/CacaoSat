import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:workmanager/workmanager.dart';

import '../data/local/database.dart';
import '../data/remote/api_client.dart';
import '../data/repositories/sync_repository.dart';

const _taskName = 'cacaosat.periodicSync';

@pragma('vm:entry-point')
void backgroundCallback() {
  Workmanager().executeTask((task, _) async {
    if (task != _taskName) return true;
    final online = !(await Connectivity().checkConnectivity())
        .contains(ConnectivityResult.none);
    if (!online) return true;

    final db = AppDatabase();
    try {
      final repo = SyncRepository(
        ApiClient(),
        db.syncDao,
        db.producerDao,
        db.parcelDao,
      );
      if ((await repo.pendingCount()) == 0) return true;
      await repo.pushAll(deviceId: 'mobile-bg');
      return true;
    } catch (_) {
      return false; // WorkManager relancera avec backoff
    } finally {
      await db.close();
    }
  });
}

/// À appeler une fois au démarrage (Android). Sur iOS, WorkManager n'offre
/// qu'un « best effort » : la sync manuelle reste le chemin principal.
Future<void> initBackgroundSync() async {
  await Workmanager().initialize(backgroundCallback);
  await Workmanager().registerPeriodicTask(
    _taskName,
    _taskName,
    frequency: const Duration(minutes: 30),
    constraints: Constraints(networkType: NetworkType.connected),
    existingWorkPolicy: ExistingPeriodicWorkPolicy.keep,
  );
}
