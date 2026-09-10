import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class ProducersScreen extends ConsumerStatefulWidget {
  const ProducersScreen({super.key});

  @override
  ConsumerState<ProducersScreen> createState() => _ProducersScreenState();
}

class _ProducersScreenState extends ConsumerState<ProducersScreen> {
  String _q = '';

  @override
  Widget build(BuildContext context) {
    final producers = ref.watch(producersStreamProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Producteurs')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/producers/new'),
        backgroundColor: CacaoTheme.orange,
        icon: const Icon(Icons.add),
        label: const Text('Ajouter'),
      ),
      body: Column(
        children: [
          const OfflineBanner(),
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search),
                labelText: 'Nom, pièce d\'identité, village',
              ),
              onChanged: (v) => setState(() => _q = v.toLowerCase()),
            ),
          ),
          Expanded(
            child: producers.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Erreur : $e')),
              data: (list) {
                final filtered = list.where((p) {
                  if (_q.isEmpty) return true;
                  return p.fullName.toLowerCase().contains(_q) ||
                      (p.nationalId ?? '').toLowerCase().contains(_q) ||
                      (p.village ?? '').toLowerCase().contains(_q);
                }).toList();
                if (filtered.isEmpty) {
                  return const Center(child: Text('Aucun producteur'));
                }
                return ListView.builder(
                  itemCount: filtered.length,
                  itemBuilder: (context, i) {
                    final p = filtered[i];
                    return ListTile(
                      title: Text(p.fullName),
                      subtitle: Text([
                        p.village ?? '',
                        p.nationalId ?? 'pièce d\'identité manquante',
                      ].where((s) => s.isNotEmpty).join(' · ')),
                      trailing: p.dirty
                          ? const Icon(Icons.sync_problem,
                              size: 18, color: CacaoTheme.riskMedium)
                          : const Icon(Icons.cloud_done,
                              size: 18, color: CacaoTheme.riskLow),
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
