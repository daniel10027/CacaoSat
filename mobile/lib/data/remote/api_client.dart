import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../core/env.dart';

/// Client HTTP CacaoSat : injection du Bearer, refresh automatique sur 401.
class ApiClient {
  ApiClient({Dio? dio, FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage(),
        _dio = dio ??
            Dio(BaseOptions(
              baseUrl: Env.apiV1,
              connectTimeout: const Duration(seconds: 8),
              receiveTimeout: const Duration(seconds: 20),
              headers: {'Content-Type': 'application/json'},
            )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (options.extra['auth'] != false) {
          final token = await _storage.read(key: _accessKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }
        handler.next(options);
      },
      onError: (e, handler) async {
        if (e.response?.statusCode == 401 &&
            e.requestOptions.extra['retried'] != true) {
          if (await _refresh()) {
            final req = e.requestOptions;
            req.extra['retried'] = true;
            final token = await _storage.read(key: _accessKey);
            req.headers['Authorization'] = 'Bearer $token';
            try {
              final res = await _dio.fetch(req);
              return handler.resolve(res);
            } catch (err) {
              return handler.next(err as DioException);
            }
          }
        }
        handler.next(e);
      },
    ));
  }

  static const _accessKey = 'cacaosat.access';
  static const _refreshKey = 'cacaosat.refresh';

  final Dio _dio;
  final FlutterSecureStorage _storage;

  Dio get raw => _dio;

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<bool> get hasSession async =>
      (await _storage.read(key: _accessKey)) != null;

  Future<bool> _refresh() async {
    final refresh = await _storage.read(key: _refreshKey);
    if (refresh == null) return false;
    try {
      final res = await Dio(BaseOptions(baseUrl: Env.apiV1)).post(
        '/auth/refresh',
        options: Options(headers: {'Authorization': 'Bearer $refresh'}),
      );
      final data = res.data as Map<String, dynamic>;
      await saveTokens(
        data['access_token'] as String,
        (data['refresh_token'] as String?) ?? refresh,
      );
      return true;
    } catch (_) {
      await clearTokens();
      return false;
    }
  }

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? query}) =>
      _dio.get<T>(path, queryParameters: query);

  Future<Response<T>> post<T>(String path, {Object? body, bool auth = true}) =>
      _dio.post<T>(path, data: body, options: Options(extra: {'auth': auth}));
}
