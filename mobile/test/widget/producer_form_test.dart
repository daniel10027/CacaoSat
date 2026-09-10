import 'dart:convert';

import 'package:cacaosat/data/local/database.dart';
import 'package:cacaosat/features/producers/producer_form_screen.dart';
import 'package:cacaosat/providers.dart';
import 'package:drift/native.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Future<AppDatabase> seededDb() async {
    final db = AppDatabase.forTesting(NativeDatabase.memory());
    await db.referenceDao.put(
      'bootstrap',
      jsonEncode({
        'cooperative': {'id': 'coop-1', 'code': 'COOP', 'name': 'Coop Test'},
        'protected_areas': {'type': 'FeatureCollection', 'features': []},
      }),
    );
    return db;
  }

  testWidgets('le formulaire refuse un nom vide et enregistre localement', (tester) async {
    final db = await seededDb();
    addTearDown(db.close);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [databaseProvider.overrideWithValue(db)],
        child: const MaterialApp(home: ProducerFormScreen()),
      ),
    );

    // Sans nom -> erreur de validation, rien en file de sync
    await tester.tap(find.text('Enregistrer'));
    await tester.pump();
    expect(find.text('Requis'), findsOneWidget);
    expect(await db.syncDao.pending(), isEmpty);

    // Avec un nom -> enregistré + mis en file
    await tester.enterText(find.byType(TextFormField).first, 'Kouamé Yao');
    await tester.tap(find.text('Enregistrer'));
    await tester.pumpAndSettle();

    final producers = await db.producerDao.all();
    expect(producers.single.fullName, 'Kouamé Yao');
    expect(producers.single.dirty, isTrue);
    expect((await db.syncDao.pending()).single.entity, 'producer');
  });
}
