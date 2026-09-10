import 'dart:convert';

import 'package:cacaosat/data/local/database.dart';
import 'package:cacaosat/features/parcels/capture_screen.dart';
import 'package:cacaosat/providers.dart';
import 'package:drift/native.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

Finder segmentLabel(String text) => find.descendant(
      of: find.byType(SegmentedButton<CaptureMode>),
      matching: find.text(text),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('la capture s\'affiche sans GPS et « Terminer » est désactivé', (tester) async {
    final db = AppDatabase.forTesting(NativeDatabase.memory());
    addTearDown(db.close);
    await db.referenceDao.put(
      'bootstrap',
      jsonEncode({
        'cooperative': {'id': 'c', 'code': 'COOP', 'name': 'Coop'},
        'protected_areas': {'type': 'FeatureCollection', 'features': []},
      }),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [databaseProvider.overrideWithValue(db)],
        child: const MaterialApp(home: CaptureScreen()),
      ),
    );
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Capturer une parcelle'), findsOneWidget);
    expect(segmentLabel('Marche'), findsOneWidget);
    expect(segmentLabel('Sommets'), findsOneWidget);
    expect(segmentLabel('Manuel'), findsOneWidget);

    final terminer = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Terminer'),
    );
    expect(terminer.onPressed, isNull); // désactivé tant qu'il y a moins de 3 sommets

    // Bascule vers « Manuel »
    await tester.tap(segmentLabel('Manuel'));
    await tester.pump();
    expect(find.text('Tapez sur la carte pour poser des sommets'), findsOneWidget);
  });
}
