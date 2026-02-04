/// ==============================================================================
/// MODULE: Chat Screen
/// ==============================================================================
///
/// AI conversational interface for the Chin Hin Employee Assistant.
/// Supports multimodal input (text, voice, images) and renders markdown responses.
///
/// Features:
/// - Real-time chat with AI assistant
/// - Voice input via speech-to-text
/// - Image attachment for visual queries
/// - Generative UI cards (e.g., LeaveConfirmationCard)
/// - Proactive nudge notifications
/// ==============================================================================
library;

import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';
import '../models/message.dart';
import '../providers/chat_provider.dart';
import '../providers/nudge_provider.dart';
import 'notification_screen.dart';
import '../providers/user_provider.dart';
import '../widgets/ai_cards.dart';
import 'live_vision_screen.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isListening = false;
  String? _selectedImageBase64;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }

  void _initSpeech() async {
    await _speech.initialize();
  }

  void _listen() async {
    if (!_isListening) {
      var status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) return;

      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) => setState(() {
            _controller.text = val.recognizedWords;
          }),
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 70,
    );
    if (image != null) {
      final bytes = await File(image.path).readAsBytes();
      setState(() {
        _selectedImageBase64 = base64Encode(bytes);
      });
    }
  }

  void _sendMessage() {
    final text = _controller.text;
    if (text.trim().isEmpty && _selectedImageBase64 == null) return;

    ref
        .read(chatProvider.notifier)
        .sendMessage(text, imageData: _selectedImageBase64);
    _controller.clear();
    setState(() {
      _selectedImageBase64 = null;
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 100,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatProvider);

    ref.listen(chatProvider, (previous, next) {
      if (next.length > (previous?.length ?? 0)) {
        _scrollToBottom();
      }
    });

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(
          "Chin Hin AI",
          style: GoogleFonts.playfairDisplay(fontWeight: FontWeight.bold),
        ),
        leading: const Icon(Icons.bubble_chart, color: Colors.white),
        actions: [
          _buildNotificationBadge(),
          IconButton(
            onPressed: () => ref.read(userProvider.notifier).logout(),
            icon: const Icon(Icons.logout, color: Colors.redAccent),
            tooltip: "Logout",
          ),
          const SizedBox(width: 8),
          const CircleAvatar(
            backgroundColor: Colors.white10,
            radius: 16,
            child: Icon(Icons.person, size: 20, color: Colors.white),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          _buildAIActionsRow(),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                return _buildMessageBubble(msg);
              },
            ),
          ),
          _buildActionIsland(),
        ],
      ),
    );
  }

  Widget _buildAIActionsRow() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      decoration: const BoxDecoration(
        color: Colors.black,
        border: Border(bottom: BorderSide(color: Colors.white10)),
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildAIActionChip(
              icon: Icons.chat_bubble_outline,
              label: "Ask AI",
              isSelected: true,
              onTap: () {},
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildAIActionChip(
              icon: Icons.visibility_rounded,
              label: "Live Assistant",
              isSelected: false,
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const LiveVisionScreen()),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAIActionChip({
    required IconData icon,
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white10 : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? Colors.white24 : Colors.white10,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.grey,
              size: 18,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: GoogleFonts.inter(
                color: isSelected ? Colors.white : Colors.grey,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildMessageBubble(Message msg) {
    bool isLeaveConfirmation = !msg.isUser && msg.text.contains("Confirm");

    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Column(
        crossAxisAlignment: msg.isUser
            ? CrossAxisAlignment.end
            : CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(12),
                topRight: const Radius.circular(12),
                bottomLeft: Radius.circular(msg.isUser ? 12 : 0),
                bottomRight: Radius.circular(msg.isUser ? 0 : 12),
              ),
              border: Border.all(
                color: msg.isUser ? Colors.white : Colors.white24,
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (msg.imageData != null) ...[
                  ClipRRect(
                    borderRadius: BorderRadius.circular(2),
                    child: Image.memory(
                      base64Decode(msg.imageData!),
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: 150,
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
                msg.isUser
                    ? Text(
                        msg.text,
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          color: Colors.white,
                        ),
                      )
                    : MarkdownBody(
                        data: msg.text,
                        styleSheet: MarkdownStyleSheet(
                          p: GoogleFonts.inter(
                            fontSize: 15,
                            color: Colors.white,
                          ),
                          listBullet: GoogleFonts.inter(color: Colors.white),
                        ),
                      ),
              ],
            ),
          ).animate().fade().scale(),

          if (isLeaveConfirmation)
            SizedBox(
              width: MediaQuery.of(context).size.width * 0.75,
              child: LeaveConfirmationCard(
                date: "Tomorrow",
                type: "Annual Leave",
                isDisabled: msg.actionExecuted,
                onConfirm: () {
                  if (!msg.actionExecuted) {
                    setState(() => msg.actionExecuted = true);
                    ref
                        .read(chatProvider.notifier)
                        .sendMessage("Yes, confirm apply.");
                  }
                },
                onCancel: () {
                  if (!msg.actionExecuted) {
                    setState(() => msg.actionExecuted = true);
                    ref
                        .read(chatProvider.notifier)
                        .sendMessage("Cancel request.");
                  }
                },
              ),
            ).animate().slideY(begin: 0.2, end: 0, duration: 400.ms).fade(),

          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildActionIsland() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 30),
      decoration: const BoxDecoration(
        color: Colors.black,
        border: Border(top: BorderSide(color: Colors.white10)),
      ),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white10,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white24, width: 1),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Row(
          children: [
            IconButton(
              onPressed: _pickImage,
              iconSize: 26,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 40, minHeight: 40),
              icon: Icon(
                Icons.add_circle_outline,
                color: _selectedImageBase64 != null
                    ? Colors.white
                    : Colors.grey,
              ),
            ),
            Expanded(
              child: TextField(
                controller: _controller,
                style: GoogleFonts.inter(color: Colors.white),
                decoration: InputDecoration(
                  hintText: "Ask anything...",
                  hintStyle: GoogleFonts.inter(color: Colors.grey),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 8),
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
            GestureDetector(
              onLongPress: _listen,
              onTap: _listen,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                child:
                    Icon(
                          _isListening ? Icons.mic : Icons.mic_none,
                          color: _isListening ? Colors.redAccent : Colors.grey,
                          size: 26,
                        )
                        .animate(target: _isListening ? 1 : 0)
                        .scale(
                          begin: const Offset(1, 1),
                          end: const Offset(1.2, 1.2),
                        ),
              ),
            ),
            Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                onPressed: _sendMessage,
                icon: const Icon(Icons.arrow_upward, color: Colors.black),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationBadge() {
    final nudges = ref.watch(nudgeProvider);
    final unreadCount = nudges.where((n) => n['is_read'] != true).length;

    return IconButton(
      icon: unreadCount > 0
          ? Badge(
              label: Text('$unreadCount'),
              backgroundColor: Colors.redAccent,
              child: const Icon(
                Icons.notifications_active,
                color: Colors.amber,
              ),
            )
          : const Icon(Icons.notifications_none, color: Colors.white),
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const NotificationScreen()),
        );
      },
    );
  }
}
