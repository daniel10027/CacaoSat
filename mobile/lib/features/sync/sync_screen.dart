import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/theme.dart';
import '../../data/local/database.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class SyncScreen extends ConsumerStatefulWidget {
  const SyncScreen({super.key});

  @override
  ConsumerState<SyncScreen> createState() => _SyncScreenState();
}

class _SyncScreenState extends ConsumerState<SyncScreen> {
  bool _running = false;

  Future<void> _sync() async {
    setState(() => _running = true);
    final messenger = ScaffoldMessenger.of(context);
    try {
      final out = await ref.read(syncRepositoryProvider).pushAll();
      messenger.showSnackBar(SnackBar(
        content: Text(out.batchId.isEmpty
            ? 'Rien à synchroniser'
            : '${out.accepted} accepté(s), ${out.rejected} rejeté(s)'),
      ));
    } catch (e) {
      messenger.showSnackBar(SnackBar(content: Text('Échec : $e')));
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final pending = ref.watch(pendingSyncCountProvider).valueOrNull ?? 0;
    final online = ref.watch(connectivityProvider).valueOrNull ?? true;

    return Scaffold(
      appBar: AppBar(title: const Text('Synchronisation')),
      body: Column(
        children: [
          const OfflineBanner(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SectionCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('$pending élément(s) en attente',
                      style: const TextStyle(
                          fontSize: 18, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 4),
                  Text(
                    online
                        ? 'Prêt à envoyer au serveur.'
                        : 'Connectez-vous à un réseau pour synchroniser.',
                    style: TextStyle(
                        color: CacaoTheme.sand.withValues(alpha: 0.6)),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: (!_running && online && pending > 0)
                          ? _sync
                          : null,
                      icon: _running
                          ? const SizedBox(
                              height: 16,
                              width: 16,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.sync),
                      label: Text(_running ? 'Envoi…' : 'Tout synchroniser'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text('Journal des envois',
                  style: TextStyle(fontWeight: FontWeight.w600)),
            ),
          ),
          Expanded(
            child: FutureBuilder<List<OutboxLogData>>(
              future: ref.read(syncRepositoryProvider).outbox(),
              builder: (context, snap) {
                final logs = snap.data ?? [];
                if (logs.isEmpty) {
                  return const Center(child: Text('Aucun envoi pour l\'instant'));
                }
                return ListView.builder(
                  itemCount: logs.length,
                  itemBuilder: (context, i) {
                    final l = logs[i];
                    return ListTile(
                      leading: Icon(
                        l.rejected == 0 ? Icons.check_circle : Icons.error,
                        color: l.rejected == 0
                            ? CacaoTheme.green
                            : CacaoTheme.riskMedium,
                      ),
                      title: Text(
                          '${l.accepted} accepté(s) · ${l.rejected} rejeté(s)'),
                      subtitle: Text(
                        DateFormat('dd/MM HH:mm:ss').format(l.sentAt),
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
