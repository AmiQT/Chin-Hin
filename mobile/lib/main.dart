/// ==============================================================================
/// MODULE: Main Application Entry
/// ==============================================================================
///
/// Entry point for the Chin Hin Employee AI Assistant mobile app.
/// Sets up Riverpod provider scope dan handles auth-based navigation.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config.dart';
import 'theme/app_theme.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'providers/user_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(const ProviderScope(child: ChinHinAIApp()));
}

class ChinHinAIApp extends ConsumerWidget {
  const ChinHinAIApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userState = ref.watch(userProvider);

    return ShadApp(
      title: 'Chin Hin Employee AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.shadDarkTheme,
      home: userState.isLoading
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : (userState.userId != null
                ? const HomeScreen()
                : const LoginScreen()),
    );
  }
}
