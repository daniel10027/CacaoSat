import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/theme.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final producers = ref.watch(producersStreamProvider);
    final parcels = ref.watch(parcelsStreamProvider);
    final pending = ref.watch(pendingSyncCountProvider).valueOrNull ?? 0;
    final email = ref.watch(sessionProvider).email;

    final producerCount = producers.valueOrNull?.length ?? 0;
    final parcelCount = parcels.valueOrNull?.length ?? 0;
    final analysed = parcels.valueOrNull
            ?.where((p) => p.eudrStatus != null)
            .length ??
        0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('CacaoSat'),
        actions: [
          const PendingSyncChip(),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async {
                try {
                  await ref.read(referenceRepositoryProvider).refresh();
                } catch (_) {}
              },
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (email != null)
                    Text('Connecté : $email',
                        style: TextStyle(
                            color: CacaoTheme.sand.withValues(alpha: 0.5),
                            fontSize: 12)),
                  const SizedBox(height: 12),
                  Row(children: [
                    _Metric(label: 'Producteurs', value: '$producerCount'),
                    const SizedBox(width: 12),
                    _Metric(label: 'Parcelles', value: '$parcelCount'),
                  ]),
                  const SizedBox(height: 12),
                  Row(children: [
                    _Metric(label: 'Analysées', value: '$analysed'),
                    const SizedBox(width: 12),
                    _Metric(
                      label: 'À synchroniser',
                      value: '$pending',
                      highlight: pending > 0,
                    ),
                  ]),
                  const SizedBox(height: 24),
                  _ActionTile(
                    icon: Icons.person_add_alt_1,
                    title: 'Nouveau producteur',
                    onTap: () => context.push('/producers/new'),
                  ),
                  _ActionTile(
                    icon: Icons.add_location_alt_outlined,
                    title: 'Nouvelle parcelle',
                    subtitle: 'Relevé GPS du contour',
                    onTap: () => context.push('/parcels/capture'),
                  ),
                  _ActionTile(
                    icon: Icons.map_outlined,
                    title: 'Parcelles',
                    subtitle: '$parcelCount enregistrées',
                    onTap: () => context.push('/parcels'),
                  ),
                  _ActionTile(
                    icon: Icons.groups_outlined,
                    title: 'Producteurs',
                    onTap: () => context.push('/producers'),
                  ),
                  _ActionTile(
                    icon: Icons.sync,
                    title: 'Synchroniser',
                    subtitle: pending > 0
                        ? '$pending élément(s) en attente'
                        : 'À jour',
                    onTap: () => context.push('/sync'),
                  ),
                  const SizedBox(height: 12),
                  _LastBootstrap(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value, this.highlight = false});
  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: SectionCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(value,
                style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: highlight ? CacaoTheme.orange : Colors.white)),
            const SizedBox(height: 2),
            Text(label,
                style: TextStyle(
                    fontSize: 12,
                    color: CacaoTheme.sand.withValues(alpha: 0.55))),
          ],
        ),
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  const _ActionTile({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.onTap,
  });
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(9),
          decoration: BoxDecoration(
            color: CacaoTheme.orange.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: CacaoTheme.orange, size: 20),
        ),
        title: Text(title,
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: subtitle == null ? null : Text(subtitle!),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}

class _LastBootstrap extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<DateTime?>(
      future: ref.read(referenceRepositoryProvider).lastBootstrap,
      builder: (context, snap) {
        final d = snap.data;
        return Text(
          d == null
              ? 'Données de référence non téléchargées — tirez pour rafraîchir'
              : 'Référence à jour : ${DateFormat('dd/MM HH:mm').format(d)}',
          style: TextStyle(
              fontSize: 11, color: CacaoTheme.sand.withValues(alpha: 0.4)),
        );
      },
    );
  }
}
