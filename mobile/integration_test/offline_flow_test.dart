import 'dart:convert';

import 'package:cacaosat/data/local/database.dart';
import 'package:cacaosat/features/home/home_screen.dart';
import 'package:cacaosat/features/producers/producer_form_screen.dart';
import 'package:cacaosat/features/sync/sync_screen.dart';
import 'package:cacaosat/providers.dart';
import 'package:drift/native.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('parcours hors-ligne : accueil → créer un producteur → file de sync', (tester) async {
    final db = AppDatabase.forTesting(NativeDatabase.memory());
    addTearDown(db.close);
    await db.referenceDao.put(
      'bootstrap',
      jsonEncode({
        'cooperative': {'id': 'coop-1', 'code': 'COOP', 'name': 'Coopérative Test'},
        'protected_areas': {'type': 'FeatureCollection', 'features': []},
      }),
    );

    Widget scoped(Widget child) => ProviderScope(
          overrides: [databaseProvider.overrideWithValue(db)],
          child: MaterialApp(
            home: child,
            routes: {
              '/producers/new': (_) => const ProducerFormScreen(),
              '/sync': (_) => const SyncScreen(),
            },
          ),
        );

    // --- Accueil : compteurs à zéro ---
    await tester.pumpWidget(scoped(const HomeScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Producteurs'), findsWidgets);
    expect(find.text('Nouveau producteur'), findsOneWidget);

    // --- Créer un producteur ---
    await tester.pumpWidget(scoped(const ProducerFormScreen()));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).first, 'Aya Konan');
    await tester.enterText(find.byType(TextFormField).at(1), 'CI0099887766');
    await tester.tap(find.text('Enregistrer'));
    await tester.pumpAndSettle();

    // --- Vérifs : local + file de sync ---
    final producers = await db.producerDao.all();
    expect(producers.single.fullName, 'Aya Konan');
    expect(producers.single.dirty, isTrue);
    final queued = await db.syncDao.pending();
    expect(queued.single.entity, 'producer');
    final payload = jsonDecode(queued.single.payload) as Map<String, dynamic>;
    expect(payload['national_id'], 'CI0099887766');
    expect(payload['cooperative_id'], 'coop-1');

    // --- Écran de synchronisation : voit l'élément en attente ---
    await tester.pumpWidget(scoped(const SyncScreen()));
    await tester.pumpAndSettle();
    expect(find.textContaining('1 élément(s) en attente'), findsOneWidget);
  });
}
