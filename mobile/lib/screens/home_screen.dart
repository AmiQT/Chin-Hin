/// ==============================================================================
/// MODULE: Home Screen
/// ==============================================================================
///
/// Main dashboard and navigation hub for the Chin Hin Employee Assistant.
/// Features a two-tab bottom navigation: Dashboard and AI Chat.
///
/// Dashboard includes:
/// - Quick action buttons (Apply Leave, Submit Claim, Book Room, etc.)
/// - All actions route to AI Chat
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';
import '../providers/chat_provider.dart';
import 'chat_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final userState = ref.watch(userProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: _currentIndex == 0
          ? _buildDashboard(context, userState)
          : const ChatScreen(),
      bottomNavigationBar: _buildBottomNav(context),
    );
  }

  Widget _buildBottomNav(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.black,
        border: Border(top: BorderSide(color: Colors.white24, width: 1)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 0, vertical: 0),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 65,
          child: Row(
            children: [
              _buildNavItem(0, "Home", Icons.home_filled),
              Container(width: 1, height: 30, color: Colors.white10),
              _buildNavItem(1, "Chin Hin AI", Icons.bubble_chart_rounded),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, String label, IconData icon) {
    final isSelected = _currentIndex == index;
    return Expanded(
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => setState(() => _currentIndex = index),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                    icon,
                    color: isSelected ? Colors.white : Colors.white24,
                    size: 26,
                  )
                  .animate(target: isSelected ? 1 : 0)
                  .scale(
                    begin: const Offset(1, 1),
                    end: const Offset(1.1, 1.1),
                    duration: 200.ms,
                  ),
              const SizedBox(height: 4),
              if (isSelected)
                Text(
                  label,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ).animate().fadeIn(duration: 200.ms)
              else
                Text(
                  label,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.normal,
                    color: Colors.white24,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, UserState userState) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(
          expandedHeight: 140,
          floating: true,
          pinned: true,
          backgroundColor: const Color(0xFF121212),
          flexibleSpace: FlexibleSpaceBar(
            titlePadding: const EdgeInsets.only(left: 16, bottom: 16),
            title: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _getGreeting().toUpperCase(),
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    color: Colors.grey,
                    letterSpacing: 1.5,
                  ),
                ),
                Text(
                  userState.fullName ??
                      userState.email?.split('@')[0] ??
                      'User',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
          actions: [
            IconButton(
              onPressed: () => _navigateToProfile(context),
              icon: const Icon(Icons.person_outline, color: Colors.white),
              tooltip: "Profile",
            ),
            const SizedBox(width: 8),
          ],
        ),

        SliverPadding(
          padding: const EdgeInsets.all(16),
          sliver: SliverToBoxAdapter(child: _buildQuickActions(context)),
        ),
      ],
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning 🌅';
    if (hour < 17) return 'Good Afternoon ☀️';
    return 'Good Evening 🌙';
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Apply Leave",
                        Icons.beach_access,
                        Colors.white,
                        () => _askAI("Nak apply cuti"),
                      )
                      .animate()
                      .fadeIn(delay: 300.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
            const SizedBox(width: 12),
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Submit Claim",
                        Icons.receipt_long,
                        Colors.white,
                        () => _askAI("Nak submit expense claim baru"),
                      )
                      .animate()
                      .fadeIn(delay: 350.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Book Room",
                        Icons.meeting_room,
                        Colors.white,
                        () => _askAI("Nak book bilik mesyuarat"),
                      )
                      .animate()
                      .fadeIn(delay: 400.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
            const SizedBox(width: 12),
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Book Transport",
                        Icons.directions_car,
                        Colors.white,
                        () => _askAI("I want to book transport"),
                      )
                      .animate()
                      .fadeIn(delay: 450.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Daily Menu",
                        Icons.restaurant,
                        Colors.white,
                        () => _askAI("What is the menu for today?"),
                      )
                      .animate()
                      .fadeIn(delay: 500.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
            const SizedBox(width: 12),
            Expanded(
              child:
                  _buildActionButton(
                        context,
                        "Energy Stats",
                        Icons.bolt,
                        Colors.white,
                        () => _askAI(
                          "Show me the energy consumption for this month",
                        ),
                      )
                      .animate()
                      .fadeIn(delay: 550.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionButton(
    BuildContext context,
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(2),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
        decoration: BoxDecoration(
          color: Colors.white10,
          borderRadius: BorderRadius.circular(2),
          border: Border.all(color: Colors.white24, width: 1),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 18),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                label,
                style: GoogleFonts.inter(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToProfile(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ProfileScreen()),
    );
  }

  void _askAI(String query) {
    setState(() => _currentIndex = 1);
    Future.microtask(() {
      ref.read(chatProvider.notifier).sendMessage(query);
    });
  }
}
