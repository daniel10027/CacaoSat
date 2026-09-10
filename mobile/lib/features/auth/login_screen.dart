import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/env.dart';
import '../../core/theme.dart';
import '../../providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController(text: 'agent1a@cacaosat.ci');
  final _password = TextEditingController(text: 'cacaosat');
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    final err = await ref
        .read(sessionProvider.notifier)
        .login(_email.text.trim(), _password.text);
    if (!mounted) return;
    setState(() {
      _loading = false;
      _error = err;
    });
    if (err == null) context.go('/home');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const _OrbitMark(),
                  const SizedBox(height: 16),
                  RichText(
                    text: const TextSpan(children: [
                      TextSpan(
                          text: 'CACAO',
                          style: TextStyle(
                              color: CacaoTheme.orange,
                              fontSize: 28,
                              fontWeight: FontWeight.w800)),
                      TextSpan(
                          text: 'SAT',
                          style: TextStyle(
                              color: CacaoTheme.green,
                              fontSize: 28,
                              fontWeight: FontWeight.w800)),
                    ]),
                  ),
                  const SizedBox(height: 8),
                  Text('Collecte terrain — conformité EUDR',
                      style: TextStyle(
                          color: CacaoTheme.sand.withValues(alpha: 0.6))),
                  const SizedBox(height: 28),
                  TextField(
                    controller: _email,
                    keyboardType: TextInputType.emailAddress,
                    decoration:
                        const InputDecoration(labelText: 'Adresse e-mail'),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _password,
                    obscureText: true,
                    decoration:
                        const InputDecoration(labelText: 'Mot de passe'),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!,
                        style: const TextStyle(
                            color: CacaoTheme.riskHigh, fontSize: 13)),
                  ],
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2, color: Colors.white))
                          : const Text('Se connecter'),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('API : ${Env.apiBaseUrl}',
                      style: TextStyle(
                          fontSize: 11,
                          color: CacaoTheme.sand.withValues(alpha: 0.35))),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _OrbitMark extends StatelessWidget {
  const _OrbitMark();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 96,
      width: 96,
      child: CustomPaint(painter: _OrbitPainter()),
    );
  }
}

class _OrbitPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero);
    canvas.save();
    canvas.translate(c.dx, c.dy);
    canvas.rotate(-0.4);
    final orbit = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = CacaoTheme.green;
    canvas.drawOval(
        Rect.fromCenter(center: Offset.zero, width: size.width, height: 34),
        orbit);
    final pod = Paint()..color = CacaoTheme.orange;
    final path = Path()
      ..moveTo(0, -22)
      ..quadraticBezierTo(16, -8, 10, 20)
      ..quadraticBezierTo(0, 30, -10, 20)
      ..quadraticBezierTo(-16, -8, 0, -22)
      ..close();
    canvas.drawPath(path, pod);
    canvas.drawCircle(Offset(-size.width / 2, 0), 4, Paint()..color = Colors.white);
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
