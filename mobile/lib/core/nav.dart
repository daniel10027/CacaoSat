import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

/// Referme l'écran courant en s'appuyant sur go_router quand il est présent,
/// et retombe sur le [Navigator] classique sinon (utile pour les tests widget
/// qui montent un écran isolé sans routeur).
void safePop<T extends Object?>(BuildContext context, [T? result]) {
  final router = GoRouter.maybeOf(context);
  if (router != null && router.canPop()) {
    router.pop(result);
    return;
  }
  final navigator = Navigator.maybeOf(context);
  if (navigator != null && navigator.canPop()) {
    navigator.pop(result);
  }
}
