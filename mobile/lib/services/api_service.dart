/// ==============================================================================
/// MODULE: API Service
/// ==============================================================================
///
/// HTTP client wrapper for all backend API communications.
/// Auto-attaches JWT token from Supabase session to all requests.
///
/// Endpoint categories:
/// - Chat: AI message handling with multimodal support
/// - Nudges: Proactive notifications
/// - Leaves: Balance, requests, types
/// - Claims: Expense submissions and categories
/// - Rooms: Booking management
/// ==============================================================================
library;

import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../config.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: Config.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final session = Supabase.instance.client.auth.currentSession;
          if (session != null) {
            options.headers['Authorization'] = 'Bearer ${session.accessToken}';
          }
          return handler.next(options);
        },
      ),
    );
  }

  Future<Map<String, dynamic>> sendMessage(
    String message, {
    required String userId,
    String? conversationId,
    String? imageData,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/chat',
        data: {
          'message': message,
          'user_id': userId,
          if (conversationId != null) 'conversation_id': conversationId,
          if (imageData != null) 'image_data': imageData,
        },
      );

      return response.data;
    } catch (e) {
      throw Exception('Failed to connect to AI: $e');
    }
  }

  Future<List<dynamic>> getNudges({bool unreadOnly = true}) async {
    try {
      final response = await _dio.get(
        '/api/v1/nudges',
        queryParameters: {'unread_only': unreadOnly},
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to fetch nudges: $e');
    }
  }

  Future<Map<String, dynamic>> markNudgeAsRead(String nudgeId) async {
    try {
      final response = await _dio.post('/api/v1/nudges/$nudgeId/read');
      return response.data;
    } catch (e) {
      throw Exception('Failed to mark nudge as read: $e');
    }
  }

  Future<Map<String, dynamic>> getUser(String userId) async {
    try {
      final response = await _dio.get('/api/v1/users/$userId');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get user: $e');
    }
  }

  Future<Map<String, dynamic>> getLeaveBalance(String userId) async {
    try {
      final response = await _dio.get('/api/v1/leaves/balance');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get leave balance: $e');
    }
  }

  Future<Map<String, dynamic>> getMyLeaves(String userId) async {
    try {
      final response = await _dio.get('/api/v1/users/$userId/leaves');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get leave requests: $e');
    }
  }

  Future<Map<String, dynamic>> applyLeave({
    required String userId,
    required String leaveTypeId,
    required String startDate,
    required String endDate,
    String? reason,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/leaves',
        data: {
          'user_id': userId,
          'leave_type_id': leaveTypeId,
          'start_date': startDate,
          'end_date': endDate,
          if (reason != null) 'reason': reason,
        },
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to apply leave: $e');
    }
  }

  Future<Map<String, dynamic>> getLeaveTypes() async {
    try {
      final response = await _dio.get('/api/v1/leaves/types');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get leave types: $e');
    }
  }

  Future<Map<String, dynamic>> getMyClaims(String userId) async {
    try {
      final response = await _dio.get('/api/v1/users/$userId/claims');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get claims: $e');
    }
  }

  Future<Map<String, dynamic>> submitClaim({
    required String userId,
    required String categoryId,
    required double amount,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/claims',
        data: {
          'user_id': userId,
          'category_id': categoryId,
          'amount': amount,
          if (description != null) 'description': description,
        },
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to submit claim: $e');
    }
  }

  Future<Map<String, dynamic>> getClaimCategories() async {
    try {
      final response = await _dio.get('/api/v1/claims/categories');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get claim categories: $e');
    }
  }

  Future<Map<String, dynamic>> getRooms() async {
    try {
      final response = await _dio.get('/api/v1/rooms');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get rooms: $e');
    }
  }

  Future<Map<String, dynamic>> bookRoom({
    required String userId,
    required String roomId,
    required String title,
    required String startTime,
    required String endTime,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/rooms/bookings',
        data: {
          'user_id': userId,
          'room_id': roomId,
          'title': title,
          'start_time': startTime,
          'end_time': endTime,
          if (description != null) 'description': description,
        },
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to book room: $e');
    }
  }

  Future<Map<String, dynamic>> getMyBookings(String userId) async {
    try {
      final response = await _dio.get(
        '/api/v1/rooms/bookings/all',
        queryParameters: {'user_id': userId},
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to get bookings: $e');
    }
  }
}
