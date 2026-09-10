import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/theme.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class ParcelsScreen extends ConsumerWidget {
  const ParcelsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final parcels = ref.watch(parcelsStreamProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Parcelles')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/parcels/capture'),
        backgroundColor: CacaoTheme.orange,
        icon: const Icon(Icons.add_location_alt_outlined),
        label: const Text('Capturer'),
      ),
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(
            child: parcels.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Erreur : $e')),
              data: (list) {
                if (list.isEmpty) {
                  return const Center(
                      child: Text('Aucune parcelle. Capturez-en une.'));
                }
                return ListView.builder(
                  itemCount: list.length,
                  itemBuilder: (context, i) {
                    final p = list[i];
                    return Card(
                      child: ListTile(
                        onTap: () => context.push('/parcels/${p.id}'),
                        title: Text(p.code,
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(
                          '${p.areaHa.toStringAsFixed(2)} ha · '
                          '${DateFormat('dd/MM/yy').format(p.collectedAt)}',
                        ),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            _StateChip(state: p.syncState),
                            if (p.score != null)
                              Text('${p.score!.toStringAsFixed(0)}/100',
                                  style: TextStyle(
                                      fontSize: 12,
                                      color: CacaoTheme.eudrColor(p.eudrStatus))),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _StateChip extends StatelessWidget {
  const _StateChip({required this.state});
  final String state;

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (state) {
      'pending' => ('local', CacaoTheme.riskMedium),
      'synced' => ('envoyée', CacaoTheme.green),
      'analyzed' => ('analysée', CacaoTheme.green),
      _ => (state, CacaoTheme.sand),
    };
    return Text(label, style: TextStyle(fontSize: 11, color: color));
  }
}
