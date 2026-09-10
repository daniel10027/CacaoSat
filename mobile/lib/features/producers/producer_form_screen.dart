import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/nav.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class ProducerFormScreen extends ConsumerStatefulWidget {
  const ProducerFormScreen({super.key});

  @override
  ConsumerState<ProducerFormScreen> createState() => _ProducerFormScreenState();
}

class _ProducerFormScreenState extends ConsumerState<ProducerFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _nationalId = TextEditingController();
  final _village = TextEditingController();
  final _phone = TextEditingController();
  String _gender = 'unknown';
  bool _saving = false;

  @override
  void dispose() {
    _name.dispose();
    _nationalId.dispose();
    _village.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    final boot = await ref.read(referenceRepositoryProvider).cachedBootstrap();
    final coopId = boot?['cooperative']?['id'] as String? ?? 'local';
    await ref.read(producerRepositoryProvider).create(
          coopId: coopId,
          fullName: _name.text.trim(),
          nationalId: _nationalId.text.trim().isEmpty ? null : _nationalId.text.trim(),
          gender: _gender,
          village: _village.text.trim().isEmpty ? null : _village.text.trim(),
          phone: _phone.text.trim().isEmpty ? null : _phone.text.trim(),
        );
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Producteur enregistré localement')),
    );
    safePop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nouveau producteur')),
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(
            child: Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  TextFormField(
                    controller: _name,
                    decoration: const InputDecoration(labelText: 'Nom complet *'),
                    validator: (v) =>
                        (v == null || v.trim().length < 2) ? 'Requis' : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _nationalId,
                    decoration: const InputDecoration(
                        labelText: 'Pièce d\'identité (CNI)'),
                  ),
                  const SizedBox(height: 14),
                  DropdownButtonFormField<String>(
                    initialValue: _gender,
                    decoration: const InputDecoration(labelText: 'Genre'),
                    items: const [
                      DropdownMenuItem(value: 'unknown', child: Text('Non précisé')),
                      DropdownMenuItem(value: 'male', child: Text('Homme')),
                      DropdownMenuItem(value: 'female', child: Text('Femme')),
                    ],
                    onChanged: (v) => setState(() => _gender = v ?? 'unknown'),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _village,
                    decoration: const InputDecoration(labelText: 'Village'),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _phone,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(labelText: 'Téléphone'),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _saving ? null : _save,
                    child: Text(_saving ? 'Enregistrement…' : 'Enregistrer'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
