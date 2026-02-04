/// ==============================================================================
/// MODULE: Chat Provider
/// ==============================================================================
///
/// AI chat state management for conversational assistant interface.
/// Maintains message history and handles API communication.
///
/// Provides:
/// - [apiServiceProvider] - Singleton access to backend API
/// - [ChatNotifier] - Message handling with multimodal support (text + images)
/// - [chatProvider] - Global chat state for widget tree access
/// ==============================================================================
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import 'user_provider.dart';

final apiServiceProvider = Provider((ref) => ApiService());

class ChatNotifier extends Notifier<List<Message>> {
  ApiService get _apiService => ref.read(apiServiceProvider);
  String? get _userId => ref.watch(userProvider).userId;

  @override
  List<Message> build() {
    // Watch user state untuk trigger rebuild bila user berubah
    ref.watch(userProvider);

    return [
      Message(
        text:
            "Hi there! I'm your Chin Hin AI Assistant.\n\nI can help you with:\n- Applying Leave 🏖️\n- Booking Rooms 🏢\n- Submitting Claims 💰\n- HR Policies (RAG) 📚\n\nWhat would you like to do today?",
        isUser: false,
        timestamp: DateTime.now(),
      ),
    ];
  }

  Future<void> sendMessage(String text, {String? imageData}) async {
    if (text.trim().isEmpty && imageData == null) return;
    final userId = _userId;
    if (userId == null) {
      state = [
        ...state,
        Message(
          text: "⚠️ Error: User not logged in.",
          isUser: false,
          timestamp: DateTime.now(),
        ),
      ];
      return;
    }

    final userMsg = Message(
      text: text,
      isUser: true,
      timestamp: DateTime.now(),
      imageData: imageData,
    );
    state = [...state, userMsg];

    final thinkingMsg = Message(
      text: "Thinking... 🤔",
      isUser: false,
      timestamp: DateTime.now(),
    );
    state = [...state, thinkingMsg];

    try {
      final response = await _apiService.sendMessage(
        text,
        userId: userId,
        imageData: imageData,
      );

      String aiText =
          "I received your message but I'm not sure how to read the response yet.";

      if (response.containsKey('response')) {
        aiText = response['response'];
      } else if (response.containsKey('data') &&
          response['data'] is Map &&
          response['data'].containsKey('response')) {
        aiText = response['data']['response'];
      }

      final newState = [...state];
      newState.removeLast();
      newState.add(
        Message(text: aiText, isUser: false, timestamp: DateTime.now()),
      );
      state = newState;
    } catch (e) {
      final newState = [...state];
      newState.removeLast();
      newState.add(
        Message(
          text: "⚠️ Server Error: ${e.toString()}",
          isUser: false,
          timestamp: DateTime.now(),
        ),
      );
      state = newState;
    }
  }
}

final chatProvider = NotifierProvider<ChatNotifier, List<Message>>(
  ChatNotifier.new,
);
