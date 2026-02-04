/// ==============================================================================
/// MODULE: Profile Screen
/// ==============================================================================
///
/// Employee profile dashboard displaying:
/// - User info and avatar
/// - Leave balance with progress bars
/// - Quick stats (pending leaves, claims)
/// - Navigation menu for history and logout
///
/// Uses [leaveBalanceProvider], [pendingLeavesProvider], [pendingClaimsProvider].
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';
import '../widgets/avatar_selector.dart';
import 'home_screen.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userState = ref.watch(userProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(
          "My Profile",
          style: GoogleFonts.playfairDisplay(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _buildProfileHeader(context, userState, ref)
                .animate()
                .fadeIn(duration: 400.ms)
                .slideY(begin: 0.1, end: 0, curve: Curves.easeOutQuad),
            const SizedBox(height: 24),

            _buildMenuSection(context, ref),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader(
    BuildContext context,
    UserState userState,
    WidgetRef ref,
  ) {
    return ShadCard(
      width: double.infinity,
      backgroundColor: Colors.black,
      border: ShadBorder.all(color: Colors.white, width: 1),
      padding: const EdgeInsets.all(24),
      child: SizedBox(
        width: double.infinity,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            AvatarDisplay(
              avatarId: userState.avatarId,
              fallbackName: userState.fullName ?? userState.email ?? 'U',
              size: 80,
              onTap: () async {
                final selected = await showAvatarSelector(
                  context,
                  currentAvatarId: userState.avatarId,
                );
                if (selected != null) {
                  await ref
                      .read(userProvider.notifier)
                      .updateAvatarId(selected);
                }
              },
            ),
            const SizedBox(height: 16),

            Text(
              userState.fullName ?? userState.email?.split('@')[0] ?? 'User',
              textAlign: TextAlign.center,
              style: GoogleFonts.playfairDisplay(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 4),

            if (userState.email != null)
              Text(
                userState.email!,
                textAlign: TextAlign.center,
                style: GoogleFonts.inter(color: Colors.grey[400]),
              ),

            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white10,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white24),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.verified, size: 16, color: Colors.white),
                  const SizedBox(width: 6),
                  Text(
                    "Active Employee",
                    style: GoogleFonts.inter(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuSection(BuildContext context, WidgetRef ref) {
    final menuItems = [
      {
        'icon': Icons.logout,
        'title': "Logout",
        'subtitle': "Sign out of your account",
        'onTap': () => _showLogoutDialog(context, ref),
        'isDestructive': true,
      },
    ];

    return Column(
      children: List.generate(menuItems.length, (index) {
        final item = menuItems[index];
        return _buildMenuItem(
              context,
              item['icon'] as IconData,
              item['title'] as String,
              item['subtitle'] as String,
              item['onTap'] as VoidCallback,
              isDestructive: item['isDestructive'] == true,
            )
            .animate()
            .fadeIn(delay: (300 + (index * 100)).ms, duration: 400.ms)
            .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad);
      }),
    );
  }

  Widget _buildMenuItem(
    BuildContext context,
    IconData icon,
    String title,
    String subtitle,
    VoidCallback onTap, {
    bool isDestructive = false,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white10,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white24, width: 1),
            ),
            child: ListTile(
              leading: Icon(
                icon,
                color: isDestructive ? Colors.redAccent : Colors.white,
              ),
              title: Text(
                title,
                style: GoogleFonts.inter(
                  color: isDestructive ? Colors.redAccent : Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
              subtitle: Text(
                subtitle,
                style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 12),
              ),
              trailing: Icon(Icons.chevron_right, color: Colors.grey[600]),
            ),
          ),
        ),
      ),
    );
  }

  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.black,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: Colors.white24),
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(
          "Logout",
          style: GoogleFonts.playfairDisplay(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          "Are you sure you want to logout?",
          style: GoogleFonts.inter(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text("Cancel", style: GoogleFonts.inter(color: Colors.grey)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              Navigator.pop(context);
              ref.read(userProvider.notifier).logout();
            },
            child: Text(
              "Logout",
              style: GoogleFonts.inter(color: Colors.redAccent),
            ),
          ),
        ],
      ),
    );
  }
}
