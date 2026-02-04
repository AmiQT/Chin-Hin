/// ==============================================================================
/// MODULE: Live Vision Screen
/// ==============================================================================
///
/// PURPOSE:
/// This module provides the UI for the real-time AI assistant feature. It uses
/// the device's camera and microphone to enable live, multimodal conversation
/// with the Gemini AI model.
///
/// NOTE: All stream subscriptions are properly tracked and cancelled in dispose()
/// to prevent "setState() called after dispose()" errors.
///
/// Uses [LiveVisionService] for WebSocket communication.
/// ==============================================================================
library;

import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/live_vision_service.dart';

class LiveVisionScreen extends StatefulWidget {
  const LiveVisionScreen({super.key});

  @override
  State<LiveVisionScreen> createState() => _LiveVisionScreenState();
}

class _LiveVisionScreenState extends State<LiveVisionScreen> {
  final LiveVisionService _liveService = LiveVisionService();
  final AudioRecorder _audioRecorder = AudioRecorder();

  CameraController? _cameraController;
  List<CameraDescription> _cameras = [];
  Timer? _frameTimer;
  StreamSubscription<List<int>>? _audioSubscription;
  StreamSubscription<String>? _textSubscription;
  StreamSubscription<bool>? _statusSubscription;
  bool _isInitializing = true;
  bool _isConnected = false;
  String _transcript = "Sila tekan 'Mula' untuk sesi Live...";

  @override
  void initState() {
    super.initState();
    _initSystem();
  }

  Future<void> _initSystem() async {
    await [Permission.camera, Permission.microphone].request();

    _cameras = await availableCameras();
    if (_cameras.isEmpty) return;

    _cameraController = CameraController(
      _cameras[0],
      ResolutionPreset.medium,
      enableAudio: false,
    );

    await _cameraController!.initialize();

    _textSubscription = _liveService.textStream.listen((text) {
      if (mounted) {
        setState(() => _transcript = text);
      }
    });

    _statusSubscription = _liveService.isConnectedStream.listen((connected) {
      debugPrint('🔌 LiveVision connection status: $connected');
      if (mounted) {
        setState(() => _isConnected = connected);
        if (!connected && _transcript.contains('Menghantar')) {
          setState(() => _transcript = 'Sambungan terputus. Cuba lagi.');
        }
      }
    });

    if (mounted) {
      setState(() => _isInitializing = false);
    }
  }

  void _toggleSession() async {
    if (_isConnected) {
      _stopSession();
    } else {
      _startSession();
    }
  }

  Future<void> _startSession() async {
    try {
      setState(() => _transcript = "Menghantar token & menyambung...");
      debugPrint('🚀 Starting LiveVision session...');

      await _liveService.connect();
      debugPrint('✅ LiveVision connected successfully');

      // Only start frame capture and audio if connection succeeded
      if (!_isConnected) {
        debugPrint('⚠️ Connection flag not set after connect()');
        return;
      }

      _frameTimer = Timer.periodic(const Duration(milliseconds: 1000), (timer) {
        _captureAndSendFrame();
      });

      if (await _audioRecorder.hasPermission()) {
        const config = RecordConfig(
          encoder: AudioEncoder.pcm16bits,
          sampleRate: 16000,
          numChannels: 1,
        );

        final stream = await _audioRecorder.startStream(config);
        _audioSubscription = stream.listen((data) {
          final base64Audio = base64Encode(data);
          _liveService.sendAudioChunk(base64Audio);
        });
        debugPrint('🎤 Audio streaming started');
      }
    } catch (e) {
      debugPrint('❌ LiveVision connection error: $e');
      if (mounted) {
        setState(() => _transcript = "Gagal menyambung: $e");
      }
    }
  }

  void _stopSession() {
    _frameTimer?.cancel();
    _audioSubscription?.cancel();
    _audioRecorder.stop();
    _liveService.disconnect();
    setState(() {
      _isConnected = false;
      _transcript = "Sesi ditamatkan.";
    });
  }

  Future<void> _captureAndSendFrame() async {
    if (_cameraController == null ||
        !_cameraController!.value.isInitialized ||
        !_isConnected) {
      return;
    }

    try {
      final XFile image = await _cameraController!.takePicture();
      final bytes = await image.readAsBytes();
      final base64String = base64Encode(bytes);

      _liveService.sendVideoFrame(base64String);
    } catch (e) {
      debugPrint('Error capturing frame: $e');
    }
  }

  @override
  void dispose() {
    _frameTimer?.cancel();
    _audioSubscription?.cancel();
    _textSubscription?.cancel();
    _statusSubscription?.cancel();
    _audioRecorder.dispose();
    _cameraController?.dispose();
    _liveService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isInitializing) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.white)),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          Positioned.fill(
            child: AspectRatio(
              aspectRatio: _cameraController!.value.aspectRatio,
              child: CameraPreview(_cameraController!),
            ),
          ),

          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.6),
                    Colors.transparent,
                    Colors.black.withValues(alpha: 0.9),
                  ],
                ),
              ),
            ),
          ),

          Positioned(
            top: 50,
            left: 20,
            right: 20,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.black,
                      border: Border.all(color: Colors.white, width: 1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.arrow_back, color: Colors.white),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.black,
                    border: Border.all(color: Colors.white, width: 1),
                    borderRadius: BorderRadius.zero,
                  ),
                  child: Row(
                    children: [
                      if (_isConnected)
                        const Icon(
                              Icons.circle,
                              color: Colors.redAccent,
                              size: 10,
                            )
                            .animate(onPlay: (c) => c.repeat())
                            .scale(
                              begin: const Offset(1, 1),
                              end: const Offset(1.5, 1.5),
                            )
                            .fadeOut(),
                      const SizedBox(width: 8),
                      Text(
                        _isConnected ? "LIVE VISION" : "OFFLINE",
                        style: GoogleFonts.playfairDisplay(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          Positioned(
            bottom: 120,
            left: 20,
            right: 20,
            child: ShadCard(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              backgroundColor: Colors.black,
              border: ShadBorder.all(color: Colors.white, width: 1),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.auto_awesome,
                        color: Colors.white,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        "GEMINI LIVE",
                        style: GoogleFonts.inter(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.0,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                        _transcript,
                        style: GoogleFonts.inter(
                          color: Colors.white,
                          fontSize: 16,
                          height: 1.4,
                        ),
                      )
                      .animate(key: ValueKey(_transcript))
                      .fadeIn()
                      .slideY(begin: 0.1, end: 0),
                ],
              ),
            ),
          ),

          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Center(
              child:
                  GestureDetector(
                        onTap: _toggleSession,
                        child: Container(
                          width: 70,
                          height: 70,
                          decoration: BoxDecoration(
                            color: _isConnected
                                ? Colors.redAccent
                                : Colors.black,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                            boxShadow: [
                              if (_isConnected)
                                BoxShadow(
                                  color: Colors.redAccent.withValues(
                                    alpha: 0.4,
                                  ),
                                  blurRadius: 20,
                                  spreadRadius: 5,
                                ),
                            ],
                          ),
                          child: Icon(
                            _isConnected
                                ? Icons.stop_rounded
                                : Icons.play_arrow_rounded,
                            color: Colors.white,
                            size: 32,
                          ),
                        ),
                      )
                      .animate(target: _isConnected ? 1 : 0)
                      .scale(
                        begin: const Offset(1, 1),
                        end: const Offset(1.1, 1.1),
                        duration: 1000.ms,
                        curve: Curves.easeInOut,
                      ),
            ),
          ),
        ],
      ),
    );
  }
}
