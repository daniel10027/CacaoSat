import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'data/local/database.dart';
import 'data/remote/api_client.dart';
import 'data/repositories/auth_repository.dart';
import 'data/repositories/parcel_repository.dart';
import 'data/repositories/producer_repository.dart';
import 'data/repositories/reference_repository.dart';
import 'data/repositories/sync_repository.dart';

/// Base locale — surchargée dans `main()` et dans les tests.
final databaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final producerDaoProvider =
    Provider<ProducerDao>((ref) => ref.watch(databaseProvider).producerDao);
final parcelDaoProvider =
    Provider<ParcelDao>((ref) => ref.watch(databaseProvider).parcelDao);
final syncDaoProvider =
    Provider<SyncDao>((ref) => ref.watch(databaseProvider).syncDao);
final referenceDaoProvider =
    Provider<ReferenceDao>((ref) => ref.watch(databaseProvider).referenceDao);

// --- Repositories ---------------------------------------------------------

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(apiClientProvider)),
);

final referenceRepositoryProvider = Provider<ReferenceRepository>(
  (ref) => ReferenceRepository(
    ref.watch(apiClientProvider),
    ref.watch(referenceDaoProvider),
    ref.watch(producerDaoProvider),
    ref.watch(parcelDaoProvider),
  ),
);

final producerRepositoryProvider = Provider<ProducerRepository>(
  (ref) => ProducerRepository(
    ref.watch(producerDaoProvider),
    ref.watch(syncDaoProvider),
  ),
);

final parcelRepositoryProvider = Provider<ParcelRepository>(
  (ref) => ParcelRepository(
    ref.watch(parcelDaoProvider),
    ref.watch(syncDaoProvider),
    ref.watch(referenceDaoProvider),
  ),
);

final syncRepositoryProvider = Provider<SyncRepository>(
  (ref) => SyncRepository(
    ref.watch(apiClientProvider),
    ref.watch(syncDaoProvider),
    ref.watch(producerDaoProvider),
    ref.watch(parcelDaoProvider),
  ),
);

// --- Flux ---------------------------------------------------------------

final producersStreamProvider = StreamProvider(
  (ref) => ref.watch(producerDaoProvider).watchAll(),
);

final parcelsStreamProvider = StreamProvider(
  (ref) => ref.watch(parcelDaoProvider).watchAll(),
);

final pendingSyncCountProvider = StreamProvider<int>(
  (ref) => ref.watch(syncDaoProvider).watchPendingCount(),
);

final connectivityProvider = StreamProvider<bool>((ref) async* {
  final c = Connectivity();
  yield !(await c.checkConnectivity()).contains(ConnectivityResult.none);
  yield* c.onConnectivityChanged
      .map((r) => !r.contains(ConnectivityResult.none));
});

// --- Session -----------------------------------------------------------

class SessionState {
  const SessionState({this.status = SessionStatus.unknown, this.email});
  final SessionStatus status;
  final String? email;

  SessionState copyWith({SessionStatus? status, String? email}) =>
      SessionState(status: status ?? this.status, email: email ?? this.email);
}

enum SessionStatus { unknown, authenticated, anonymous }

class SessionController extends StateNotifier<SessionState> {
  SessionController(this._auth, this._api) : super(const SessionState()) {
    _bootstrap();
  }

  final AuthRepository _auth;
  final ApiClient _api;

  Future<void> _bootstrap() async {
    if (await _api.hasSession) {
      final me = await _auth.me();
      state = me.fold(
        (u) => SessionState(status: SessionStatus.authenticated, email: u.email),
        (_) => const SessionState(status: SessionStatus.anonymous),
      );
    } else {
      state = const SessionState(status: SessionStatus.anonymous);
    }
  }

  Future<String?> login(String email, String password) async {
    final res = await _auth.login(email, password);
    return res.fold((_) {
      state = SessionState(status: SessionStatus.authenticated, email: email);
      return null;
    }, (f) => f.message);
  }

  Future<void> logout() async {
    await _api.clearTokens();
    state = const SessionState(status: SessionStatus.anonymous);
  }
}

final sessionProvider =
    StateNotifierProvider<SessionController, SessionState>((ref) {
  return SessionController(
    ref.watch(authRepositoryProvider),
    ref.watch(apiClientProvider),
  );
});
