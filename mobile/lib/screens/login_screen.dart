/// ==============================================================================
/// MODULE: Login Screen
/// ==============================================================================
///
/// Authentication screen supporting sign-in and sign-up flows.
/// Handles email/password validation and Supabase auth via [userProvider].
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _fullNameController = TextEditingController();
  bool _isSignUp = false;
  bool _isLoading = false;

  void _submit() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final fullName = _fullNameController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter email and password')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      if (_isSignUp) {
        await ref
            .read(userProvider.notifier)
            .signUp(
              email,
              password,
              fullName: fullName.isNotEmpty ? fullName : null,
            );
      } else {
        await ref.read(userProvider.notifier).signIn(email, password);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: ${e.toString()}')));
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final userState = ref.watch(userProvider);

    if (userState.error != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(userState.error!)));
      });
    }

    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.bubble_chart,
                size: 80,
                color: Colors.white,
              ).animate().scale(duration: 600.ms),
              const SizedBox(height: 20),
              Text(
                "Chin Hin AI",
                style: GoogleFonts.playfairDisplay(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ).animate().fadeIn().moveY(begin: 20, end: 0),
              const SizedBox(height: 10),
              Text(
                "Your Digital Employee Assistant",
                style: GoogleFonts.inter(color: Colors.grey[400]),
              ).animate().fadeIn(delay: 200.ms),
              const SizedBox(height: 50),

              if (_isSignUp)
                ShadInput(
                  controller: _fullNameController,
                  placeholder: const Text("Full Name"),
                  leading: const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Icon(
                      Icons.person_outline,
                      size: 16,
                      color: Colors.grey,
                    ),
                  ),
                ).animate().fadeIn(delay: 300.ms),
              if (_isSignUp) const SizedBox(height: 16),

              ShadInput(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                placeholder: const Text("Email"),
                leading: const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Icon(
                    Icons.email_outlined,
                    size: 16,
                    color: Colors.grey,
                  ),
                ),
              ).animate().fadeIn(delay: 400.ms),
              const SizedBox(height: 16),

              ShadInput(
                controller: _passwordController,
                obscureText: true,
                placeholder: const Text("Password"),
                leading: const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Icon(Icons.lock_outline, size: 16, color: Colors.grey),
                ),
              ).animate().fadeIn(delay: 500.ms),
              const SizedBox(height: 24),

              ShadButton(
                width: double.infinity,
                onPressed: _isLoading ? null : _submit,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.black,
                        ),
                      )
                    : Text(
                        _isSignUp ? "Create Account" : "Sign In",
                        style: GoogleFonts.inter(
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
              ).animate().fadeIn(delay: 600.ms),

              const SizedBox(height: 20),

              TextButton(
                onPressed: () {
                  setState(() => _isSignUp = !_isSignUp);
                },
                child: Text(
                  _isSignUp
                      ? "Already have an account? Sign In"
                      : "Don't have an account? Sign Up",
                  style: GoogleFonts.inter(color: Colors.grey[400]),
                ),
              ).animate().fadeIn(delay: 700.ms),
            ],
          ),
        ),
      ),
    );
  }
}
