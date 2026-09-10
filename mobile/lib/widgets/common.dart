import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/theme.dart';
import '../providers.dart';

/// Bannière « hors-ligne » affichée en haut des écrans.
class OfflineBanner extends ConsumerWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final online = ref.watch(connectivityProvider).valueOrNull ?? true;
    if (online) return const SizedBox.shrink();
    return Container(
      width: double.infinity,
      color: CacaoTheme.riskMedium.withValues(alpha: 0.18),
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      child: const Row(
        children: [
          Icon(Icons.cloud_off, size: 15, color: CacaoTheme.riskMedium),
          SizedBox(width: 8),
          Text('Hors ligne — les relevés sont enregistrés localement',
              style: TextStyle(fontSize: 12, color: CacaoTheme.riskMedium)),
        ],
      ),
    );
  }
}

class PendingSyncChip extends ConsumerWidget {
  const PendingSyncChip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(pendingSyncCountProvider).valueOrNull ?? 0;
    if (count == 0) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ActionChip(
        avatar: const Icon(Icons.sync, size: 16, color: Colors.white),
        label: Text('$count', style: const TextStyle(color: Colors.white)),
        backgroundColor: CacaoTheme.orange,
        onPressed: () => Navigator.of(context).pushNamed('/sync'),
      ),
    );
  }
}

class SectionCard extends StatelessWidget {
  const SectionCard({super.key, required this.child, this.padding});
  final Widget child;
  final EdgeInsets? padding;

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: padding ?? const EdgeInsets.all(16),
          child: child,
        ),
      );
}

class EudrTag extends StatelessWidget {
  const EudrTag({super.key, required this.status});
  final String? status;

  @override
  Widget build(BuildContext context) {
    final c = CacaoTheme.eudrColor(status);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: c.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: c.withValues(alpha: 0.4)),
      ),
      child: Text(
        CacaoTheme.eudrLabel(status),
        style: TextStyle(color: c, fontSize: 12, fontWeight: FontWeight.w600),
      ),
    );
  }
}
