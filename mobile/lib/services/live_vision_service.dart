/// ==============================================================================
/// MODULE: Live Vision Service
/// ==============================================================================
///
/// PURPOSE:
/// This module manages the real-time multimodal communication layer between the
/// mobile application and the Gemini Live API. It handles the full lifecycle of
/// the WebSocket connection, including authentication, session setup, and
/// bidirectional data streaming (audio/video input -> text/audio/tool output).
///
/// DEPENDENCIES:
/// - Dio: For fetching ephemeral tokens from the backend.
/// - WebSocketChannel: For maintaining the persistent connection to Gemini.
/// - Supabase: For user authentication context.
///
/// KEY COMPONENTS:
/// - Connection Management: Connects, maintains, and cleanly closes WebSockets.
/// - Input Streaming: Encodes and streams Camera (JPEG) and Mic (PCM) data.
/// - Output Handling: Routes Gemini's responses (Text, Audio, Tools) to
///   appropriate streams for the UI to consume.
///
/// USAGE:
/// Used primarily by [LiveVisionScreen]. Call [connect()] to start, then listen
/// to [textStream], [audioStream], etc. Don't forget to call [disconnect()]!
/// ==============================================================================
library;

import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config.dart';

/// ----------------------------------------------------------------------------
/// CLASS: Live Vision Service
/// ----------------------------------------------------------------------------
/// Acts as the central controller for the "Live Vision" feature.
/// Maintains internal state (_isConnected) and exposes broadcast streams
/// so multiple UI components can listen to updates if needed.
class LiveVisionService {
  WebSocketChannel? _channel;
  final _dio = Dio(BaseOptions(baseUrl: Config.baseUrl));

  // Stream controllers for different data types
  final _textController = StreamController<String>.broadcast();
  final _audioController = StreamController<List<int>>.broadcast();
  final _functionCallController =
      StreamController<Map<String, dynamic>>.broadcast();
  final _statusController = StreamController<bool>.broadcast();

  Stream<String> get textStream => _textController.stream;
  Stream<List<int>> get audioStream => _audioController.stream;
  Stream<Map<String, dynamic>> get functionCallStream =>
      _functionCallController.stream;
  Stream<bool> get isConnectedStream => _statusController.stream;

  bool _isConnected = false;

  LiveVisionService() {
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

  /// 1. Get Ephemeral Token from our Backend
  Future<Map<String, dynamic>> _getEphemeralToken() async {
    try {
      final response = await _dio.get('/api/v1/live/token');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get live vision token: $e');
    }
  }

  /// --------------------------------------------------------------------------
  /// METHOD: Connect
  /// --------------------------------------------------------------------------
  /// Initializes the Gemini Live session in three steps:
  /// 1. Fetch an ephemeral token from our secure backend (to avoid exposing keys).
  /// 2. Establish a WebSocket connection using the token.
  /// 3. Send the initial "Setup" configuration (system instructions, tools, etc).
  ///
  /// Throws an exception if connection fails.
  Future<void> connect() async {
    if (_isConnected) return;

    try {
      debugPrint('🔐 [LiveVision] Fetching ephemeral token...');
      final data = await _getEphemeralToken();
      final token = data['token'];
      final wsUrl = data['websocket_url'];

      debugPrint(
        '✅ [LiveVision] Token received: ${token?.substring(0, 20)}...',
      );
      debugPrint('🌐 [LiveVision] WebSocket URL: $wsUrl');

      final uri = Uri.parse('$wsUrl?key=$token');

      debugPrint('🔌 [LiveVision] Connecting to: $uri');
      _channel = WebSocketChannel.connect(uri);

      // Wait for the WebSocket to be ready
      await _channel!.ready;
      debugPrint('✅ [LiveVision] WebSocket connected successfully!');

      _isConnected = true;
      _statusController.add(true);

      _channel!.stream.listen(
        (message) {
          debugPrint(
            '📨 [LiveVision] Received message: ${message.toString().substring(0, 100)}...',
          );
          _handleGeminiMessage(message);
        },
        onDone: () {
          debugPrint('🔴 [LiveVision] WebSocket closed (onDone)');
          _handleDisconnect();
        },
        onError: (err) {
          debugPrint('❌ [LiveVision] WebSocket error: $err');
          _handleDisconnect(error: err);
        },
      );

      _sendSetup();
      debugPrint('📤 [LiveVision] Setup message sent');
    } catch (e) {
      debugPrint('💥 [LiveVision] Connection error: $e');
      _handleDisconnect(error: e);
      rethrow;
    }
  }

  void _sendSetup() {
    // Simplified setup message for testing - minimal config
    final setupMessage = {
      "setup": {
        "model": "models/gemini-2.5-flash-native-audio-preview-12-2025",
        "generationConfig": {
          "responseModalities": ["AUDIO"],
        },
        "systemInstruction": {
          "parts": [
            {
              "text":
                  "You are a helpful AI assistant. Respond in Bahasa Melayu.",
            },
          ],
        },
      },
    };

    debugPrint('📝 [LiveVision] Setup message: ${jsonEncode(setupMessage)}');
    _channel?.sink.add(jsonEncode(setupMessage));
  }

  /// --------------------------------------------------------------------------
  /// METHOD: Message Handler
  /// --------------------------------------------------------------------------
  /// Parses raw JSON messages from Gemini.
  ///
  /// HANDLES:
  /// - [setupComplete]: Acknowledges that session config was accepted.
  /// - [serverContent]: Standard text/audio responses.
  ///   - [modelTurn]: The AI's turn to speak/write.
  ///     - text: Pushed to [textStream].
  ///     - inlineData: Audio chunks, pushed to [audioStream].
  /// - [toolCall]: Requests from AI to exact actions (e.g., apply leave).
  ///   - Pushed to [functionCallStream].
  void _handleGeminiMessage(dynamic message) {
    try {
      // Handle both String and Uint8List (binary) messages
      String jsonString;
      if (message is String) {
        jsonString = message;
      } else if (message is List<int>) {
        jsonString = utf8.decode(message);
      } else {
        debugPrint('⚠️ Unknown message type: ${message.runtimeType}');
        return;
      }

      final data = jsonDecode(jsonString);
      debugPrint(
        '📩 [LiveVision] Parsed: ${jsonString.substring(0, jsonString.length.clamp(0, 200))}...',
      );

      // Handle setup completion
      if (data.containsKey('setupComplete')) {
        debugPrint('✅ [LiveVision] Setup complete! Session ready.');
        return;
      }

      if (data.containsKey('serverContent')) {
        final content = data['serverContent'];

        if (content != null && content.containsKey('modelTurn')) {
          final modelTurn = content['modelTurn'];
          if (modelTurn != null && modelTurn.containsKey('parts')) {
            final parts = modelTurn['parts'] as List;
            for (var part in parts) {
              if (part.containsKey('text')) {
                _textController.add(part['text']);
                debugPrint('💬 [LiveVision] Text: ${part['text']}');
              }
              if (part.containsKey('inlineData')) {
                final audioBase64 = part['inlineData']['data'];
                _audioController.add(base64Decode(audioBase64));
              }
            }
          }
        }
      }

      if (data.containsKey('toolCall')) {
        _functionCallController.add(data['toolCall']);
        debugPrint('🔧 [LiveVision] Tool call received');
      }
    } catch (e) {
      debugPrint('❌ Error parsing Gemini message: $e');
    }
  }

  /// --------------------------------------------------------------------------
  /// SECTION: Input Streaming
  /// --------------------------------------------------------------------------
  /// The following methods are called frequently (e.g., every frame or audio chunk)
  /// to stream user context to the AI.

  /// Sends a single JPEG frame (Base64 encoded) to the model.
  /// The 'mime_type' is hardcoded to 'image/jpeg'.
  void sendVideoFrame(String base64Image) {
    if (!_isConnected) return;

    final message = {
      "realtime_input": {
        "media_chunks": [
          {"data": base64Image, "mime_type": "image/jpeg"},
        ],
      },
    };

    _channel?.sink.add(jsonEncode(message));
  }

  /// Send real-time audio chunk (base64)
  void sendAudioChunk(String base64Audio) {
    if (!_isConnected) return;

    final message = {
      "realtime_input": {
        "media_chunks": [
          {"data": base64Audio, "mime_type": "audio/pcm;rate=16000"},
        ],
      },
    };

    _channel?.sink.add(jsonEncode(message));
  }

  void _handleDisconnect({dynamic error}) {
    _isConnected = false;
    _statusController.add(false);
    if (error != null) {
      debugPrint('LiveVision WebSocket Error/Done: $error');
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _handleDisconnect();
  }

  void dispose() {
    disconnect();
    _textController.close();
    _audioController.close();
    _functionCallController.close();
    _statusController.close();
  }
}
