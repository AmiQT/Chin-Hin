/// ==============================================================================
/// MODULE: Main Application Entry
/// ==============================================================================
///
/// Entry point for the Chin Hin Employee AI Assistant mobile app.
/// Initializes Supabase and sets up Riverpod provider scope.
/// Handles auth-based navigation between Login and Home screens.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/supabase_config.dart';
import 'theme/app_theme.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'providers/user_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: SupabaseConfig.url,
    anonKey: SupabaseConfig.anonKey,
  );

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
