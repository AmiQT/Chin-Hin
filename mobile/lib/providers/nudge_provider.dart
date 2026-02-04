/// ==============================================================================
/// MODULE: Nudge Provider
/// ==============================================================================
///
/// Proactive notification state management. Fetches and manages AI-generated
/// reminders/nudges for users (e.g., pending approvals, upcoming deadlines).
///
/// Uses [ApiService] to fetch and mark nudges as read.
/// ==============================================================================
library;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import 'chat_provider.dart';

class NudgeNotifier extends Notifier<List<dynamic>> {
  late final ApiService _apiService;

  @override
  List<dynamic> build() {
    _apiService = ref.read(apiServiceProvider);
    return [];
  }

  /// Fetch only unread nudges (for badge count)
  Future<void> fetchNudges() async {
    try {
      final nudges = await _apiService.getNudges(unreadOnly: true);
      state = nudges;
    } catch (e) {
      debugPrint('Error fetching nudges: $e');
    }
  }

  /// Fetch all nudges including read ones (for history page)
  Future<void> fetchAllNudges() async {
    try {
      final nudges = await _apiService.getNudges(unreadOnly: false);
      state = nudges;
    } catch (e) {
      debugPrint('Error fetching all nudges: $e');
    }
  }

  /// Mark a nudge as read and update local state
  Future<void> markAsRead(String nudgeId) async {
    try {
      await _apiService.markNudgeAsRead(nudgeId);
      // Update local state to mark as read instead of removing
      state = state.map((n) {
        if (n['id'] == nudgeId) {
          return {...n, 'is_read': true};
        }
        return n;
      }).toList();
    } catch (e) {
      debugPrint('Error marking nudge as read: $e');
    }
  }

  /// Get count of unread nudges
  int get unreadCount => state.where((n) => n['is_read'] != true).length;
}

final nudgeProvider = NotifierProvider<NudgeNotifier, List<dynamic>>(
  NudgeNotifier.new,
);
