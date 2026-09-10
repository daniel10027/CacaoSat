import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/env.dart';
import '../../providers.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final email = ref.watch(sessionProvider).email;
    final online = ref.watch(connectivityProvider).valueOrNull ?? true;

    return Scaffold(
      appBar: AppBar(title: const Text('Réglages')),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.person_outline),
            title: const Text('Compte'),
            subtitle: Text(email ?? '—'),
          ),
          ListTile(
            leading: const Icon(Icons.link),
            title: const Text('URL de l\'API'),
            subtitle: Text(Env.apiBaseUrl),
          ),
          ListTile(
            leading: Icon(online ? Icons.wifi : Icons.wifi_off),
            title: const Text('Réseau'),
            subtitle: Text(online ? 'En ligne' : 'Hors ligne'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.cloud_download_outlined),
            title: const Text('Rafraîchir les données de référence'),
            onTap: () async {
              final messenger = ScaffoldMessenger.of(context);
              try {
                await ref.read(referenceRepositoryProvider).refresh();
                messenger.showSnackBar(
                    const SnackBar(content: Text('Données de référence à jour')));
              } catch (e) {
                messenger.showSnackBar(
                    SnackBar(content: Text('Échec : $e')));
              }
            },
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.redAccent),
            title: const Text('Se déconnecter',
                style: TextStyle(color: Colors.redAccent)),
            onTap: () async {
              await ref.read(sessionProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
    );
  }
}
