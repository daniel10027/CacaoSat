import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';
import 'core/background_sync.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (Platform.isAndroid) {
    try {
      await initBackgroundSync();
    } catch (_) {
      // La sync manuelle reste disponible si WorkManager échoue.
    }
  }

  runApp(const ProviderScope(child: CacaoSatApp()));
}
