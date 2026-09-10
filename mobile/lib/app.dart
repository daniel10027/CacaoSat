import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router.dart';
import 'core/theme.dart';

class CacaoSatApp extends ConsumerWidget {
  const CacaoSatApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'CacaoSat',
      debugShowCheckedModeBanner: false,
      theme: CacaoTheme.dark,
      routerConfig: router,
    );
  }
}
