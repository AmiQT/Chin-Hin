/// ==============================================================================
/// MODULE: User Provider
/// ==============================================================================
///
/// Authentication state management using Riverpod 2.0 Notifier pattern.
/// Handles user session via Supabase Auth with automatic state sync.
///
/// Provides:
/// - [UserState] - Immutable auth state (userId, email, fullName, isLoading)
/// - [UserNotifier] - Methods: signUp, signIn, signOut, login (legacy)
/// - [userProvider] - Global provider for widget tree access
/// ==============================================================================
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

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

class UserNotifier extends Notifier<UserState> {
  @override
  UserState build() {
    _initAuthListener();
    return UserState(isLoading: true);
  }

  void _initAuthListener() {
    final supabase = Supabase.instance.client;

    final session = supabase.auth.currentSession;
    if (session != null) {
      _setUserFromSession(session);
    } else {
      state = UserState(isLoading: false);
    }

    supabase.auth.onAuthStateChange.listen((data) {
      final session = data.session;
      if (session != null) {
        _setUserFromSession(session);
      } else {
        state = UserState(isLoading: false);
      }
    });
  }

  void _setUserFromSession(Session session) {
    final user = session.user;
    state = UserState(
      userId: user.id,
      email: user.email,
      fullName: user.userMetadata?['full_name'] as String?,
      avatarId: user.userMetadata?['avatar_id'] as String?,
      isLoading: false,
    );
  }

  Future<void> updateAvatarId(String avatarId) async {
    final supabase = Supabase.instance.client;
    await supabase.auth.updateUser(
      UserAttributes(data: {'avatar_id': avatarId}),
    );
    state = state.copyWith(avatarId: avatarId);
  }

  Future<void> signUp(String email, String password, {String? fullName}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final supabase = Supabase.instance.client;
      await supabase.auth.signUp(
        email: email,
        password: password,
        data: {'full_name': fullName ?? email.split('@')[0]},
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> signIn(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final supabase = Supabase.instance.client;
      await supabase.auth.signInWithPassword(email: email, password: password);
      // Auth listener will handle state update
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> signOut() async {
    final supabase = Supabase.instance.client;
    await supabase.auth.signOut();
    state = UserState(isLoading: false);
  }

  Future<void> login(String userId) async {
    state = UserState(userId: userId, isLoading: false);
  }

  Future<void> logout() async {
    await signOut();
  }
}

final userProvider = NotifierProvider<UserNotifier, UserState>(
  UserNotifier.new,
);
