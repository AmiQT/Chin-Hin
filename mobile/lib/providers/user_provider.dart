/// ==============================================================================
/// MODULE: User Provider
/// ==============================================================================
///
/// Authentication state management menggunakan Riverpod Notifier pattern.
/// Supabase dah dibuang — guna backend REST API + SharedPreferences. ??
///
/// Provides:
/// - [UserState] - Immutable auth state (userId, email, fullName, isLoading)
/// - [UserNotifier] - Methods: signUp, signIn, signOut, login (legacy)
/// - [userProvider] - Global provider untuk widget tree
/// ==============================================================================
library;

import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config.dart';

// ================================================
// CONSTANTS
// ================================================

const _kTokenKey = 'auth_token';
const _kUserIdKey = 'auth_user_id';
const _kEmailKey = 'auth_email';
const _kFullNameKey = 'auth_full_name';

// ================================================
// USER STATE
// ================================================

class UserState {
  final String? userId;
  final String? email;
  final String? fullName;
  final String? avatarId;
  final bool isLoading;
  final String? error;

  UserState({
    this.userId,
    this.email,
    this.fullName,
    this.avatarId,
    this.isLoading = true,
    this.error,
  });

  UserState copyWith({
    String? userId,
    String? email,
    String? fullName,
    String? avatarId,
    bool? isLoading,
    String? error,
  }) {
    return UserState(
      userId: userId ?? this.userId,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      avatarId: avatarId ?? this.avatarId,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// ================================================
// USER NOTIFIER
// ================================================

class UserNotifier extends Notifier<UserState> {
  late final Dio _dio;

  @override
  UserState build() {
    _dio = Dio(BaseOptions(baseUrl: Config.baseUrl));

    // Dev / local mode — guna test user terus
    if (Config.isLocal) {
      return UserState(
        userId: Config.testUserId,
        email: 'test@chinhin.com',
        fullName: 'Test User (Local)',
        isLoading: false,
      );
    }

    // Load stored session
    _loadStoredSession();
    return UserState(isLoading: true);
  }

  // ------------------------------------------------
  // Load session dari SharedPreferences
  // ------------------------------------------------
  Future<void> _loadStoredSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getString(_kUserIdKey);
      final email = prefs.getString(_kEmailKey);
      final fullName = prefs.getString(_kFullNameKey);

      if (userId != null) {
        state = UserState(
          userId: userId,
          email: email,
          fullName: fullName,
          isLoading: false,
        );
      } else {
        state = UserState(isLoading: false);
      }
    } catch (e) {
      state = UserState(isLoading: false, error: e.toString());
    }
  }

  // ------------------------------------------------
  // Simpan session ke SharedPreferences
  // ------------------------------------------------
  Future<void> _saveSession({
    required String token,
    required String userId,
    required String email,
    required String fullName,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kTokenKey, token);
    await prefs.setString(_kUserIdKey, userId);
    await prefs.setString(_kEmailKey, email);
    await prefs.setString(_kFullNameKey, fullName);
  }

  // ------------------------------------------------
  // Clear session dari SharedPreferences
  // ------------------------------------------------
  Future<void> _clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_kTokenKey);
    await prefs.remove(_kUserIdKey);
    await prefs.remove(_kEmailKey);
    await prefs.remove(_kFullNameKey);
  }

  // ------------------------------------------------
  // Sign Up
  // ------------------------------------------------
  Future<void> signUp(String email, String password, {String? fullName}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _dio.post('/api/v1/auth/signup', data: {
        'email': email,
        'password': password,
        if (fullName != null) 'full_name': fullName,
      });
      final data = response.data;
      if (data['success'] == true) {
        await _saveSession(
          token: data['access_token'],
          userId: data['user_id'],
          email: email,
          fullName: data['full_name'] ?? fullName ?? email.split('@')[0],
        );
        state = UserState(
          userId: data['user_id'],
          email: email,
          fullName: data['full_name'],
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false, error: data['message']);
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['detail'] ?? e.message ?? 'Signup gagal';
      state = state.copyWith(isLoading: false, error: msg.toString());
    }
  }

  // ------------------------------------------------
  // Sign In
  // ------------------------------------------------
  Future<void> signIn(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _dio.post('/api/v1/auth/login', data: {
        'email': email,
        'password': password,
      });
      final data = response.data;
      if (data['success'] == true) {
        await _saveSession(
          token: data['access_token'],
          userId: data['user_id'],
          email: email,
          fullName: data['full_name'] ?? email.split('@')[0],
        );
        state = UserState(
          userId: data['user_id'],
          email: email,
          fullName: data['full_name'],
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false, error: data['message']);
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['detail'] ?? e.message ?? 'Login gagal';
      state = state.copyWith(isLoading: false, error: msg.toString());
    }
  }

  // ------------------------------------------------
  // Sign Out
  // ------------------------------------------------
  Future<void> signOut() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_kTokenKey);
      if (token != null) {
        await _dio.post('/api/v1/auth/logout', data: {'access_token': token});
      }
    } catch (_) {
      // Ignore logout API errors — clear local session anyway
    }
    await _clearSession();
    state = UserState(isLoading: false);
  }

  // ------------------------------------------------
  // Update Avatar ID (local only)
  // ------------------------------------------------
  Future<void> updateAvatarId(String avatarId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_avatar_id', avatarId);
    state = state.copyWith(avatarId: avatarId);
  }

  // ------------------------------------------------
  // Legacy helpers
  // ------------------------------------------------
  Future<void> login(String userId) async {
    state = UserState(userId: userId, isLoading: false);
  }

  Future<void> logout() async => signOut();
}

// ================================================
// PROVIDER
// ================================================

final userProvider = NotifierProvider<UserNotifier, UserState>(
  UserNotifier.new,
);
