import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/login_screen.dart';
import '../features/home/home_screen.dart';
import '../features/parcels/capture_screen.dart';
import '../features/parcels/parcel_detail_screen.dart';
import '../features/parcels/parcels_screen.dart';
import '../features/producers/producer_form_screen.dart';
import '../features/producers/producers_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/sync/sync_screen.dart';
import '../providers.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/home',
    refreshListenable: _SessionListenable(ref),
    redirect: (context, state) {
      final status = ref.read(sessionProvider).status;
      final atLogin = state.matchedLocation == '/login';
      if (status == SessionStatus.unknown) return null;
      if (status == SessionStatus.anonymous) return atLogin ? null : '/login';
      if (atLogin) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/producers', builder: (_, __) => const ProducersScreen()),
      GoRoute(
        path: '/producers/new',
        builder: (_, __) => const ProducerFormScreen(),
      ),
      GoRoute(path: '/parcels', builder: (_, __) => const ParcelsScreen()),
      GoRoute(path: '/parcels/capture', builder: (_, __) => const CaptureScreen()),
      GoRoute(
        path: '/parcels/:id',
        builder: (_, s) => ParcelDetailScreen(parcelId: s.pathParameters['id']!),
      ),
      GoRoute(path: '/sync', builder: (_, __) => const SyncScreen()),
      GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
    ],
  );
});

class _SessionListenable extends ChangeNotifier {
  _SessionListenable(Ref ref) {
    ref.listen(sessionProvider, (_, __) => notifyListeners());
  }
}
