/// ==============================================================================
/// MODULE: Message Model
/// ==============================================================================
///
/// Data model for chat messages in the AI assistant interface.
/// Supports text, images (base64), and action state tracking.
/// ==============================================================================
library;

class Message {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? imageData;
  bool actionExecuted;

  Message({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.imageData,
    this.actionExecuted = false,
  });
}
