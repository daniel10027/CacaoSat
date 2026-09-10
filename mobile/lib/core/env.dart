/// Configuration injectée au build : `--dart-define=API_BASE_URL=http://<ip>:8000`.
class Env {
  const Env._();

  /// URL de base de l'API CacaoSat.
  /// - émulateur Android : `http://10.0.2.2:8000`
  /// - appareil physique : IP LAN de la machine (fournie par `scripts/dev.sh`)
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static String get apiV1 => '$apiBaseUrl/api/v1';

  static const int schemaVersion = 1;
}
