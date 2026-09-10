import 'package:dio/dio.dart';

import '../../core/result.dart';
import '../remote/api_client.dart';

class CurrentUser {
  const CurrentUser({required this.email, required this.role, this.cooperativeId});
  final String email;
  final String role;
  final String? cooperativeId;
}

class AuthRepository {
  AuthRepository(this._api);
  final ApiClient _api;

  Future<Result<CurrentUser>> login(String email, String password) async {
    try {
      final res = await _api.post<Map<String, dynamic>>(
        '/auth/login',
        auth: false,
        body: {'email': email, 'password': password},
      );
      final data = res.data!;
      await _api.saveTokens(
        data['access_token'] as String,
        data['refresh_token'] as String,
      );
      return await me();
    } on DioException catch (e) {
      final msg = e.response?.data is Map
          ? ((e.response!.data['error']?['message'] as String?) ??
              'Identifiants invalides.')
          : 'Connexion impossible. Vérifiez le réseau et l\'URL de l\'API.';
      return Err(Failure(msg, code: 'login_failed', cause: e));
    }
  }

  Future<Result<CurrentUser>> me() async {
    try {
      final res = await _api.get<Map<String, dynamic>>('/auth/me');
      final d = res.data!;
      return Ok(CurrentUser(
        email: d['email'] as String,
        role: d['role'] as String,
        cooperativeId: d['cooperative_id'] as String?,
      ));
    } on DioException catch (e) {
      return Err(Failure('Session expirée.', code: 'no_session', cause: e));
    }
  }
}
