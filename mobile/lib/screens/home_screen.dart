/// ==============================================================================
/// MODULE: Home Screen
/// ==============================================================================
///
/// Main dashboard and navigation hub for the Chin Hin Employee Assistant.
/// Features a two-tab bottom navigation: Dashboard and AI Chat.
///
/// Dashboard includes:
/// - Leave balance overview with pending/used breakdown
/// - Quick stats for pending leaves and claims
/// - Quick action buttons (Apply Leave, Submit Claim, Book Room)
///
/// Uses [leaveBalanceProvider], [pendingLeavesProvider], [pendingClaimsProvider]
/// for real-time dashboard data.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';
import '../providers/chat_provider.dart';
import 'chat_screen.dart';
import 'leave_request_screen.dart';
import 'claim_submit_screen.dart';
import 'room_booking_screen.dart';
import 'profile_screen.dart';

final leaveBalanceProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, userId) async {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getLeaveBalance(userId);
    });

final pendingLeavesProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, userId) async {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getMyLeaves(userId);
    });

final pendingClaimsProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, userId) async {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getMyClaims(userId);
    });

final pendingBookingsProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, userId) async {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getMyBookings(userId);
    });

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
    final userId = userState.userId ?? '';

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: _currentIndex == 0
          ? _buildDashboard(context, userId, userState)
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
          onTap: () {
            if (index == 0 && _currentIndex != 0) {
              final userId = ref.read(userProvider).userId ?? '';
              if (userId.isNotEmpty) {
                ref.invalidate(leaveBalanceProvider(userId));
                ref.invalidate(pendingLeavesProvider(userId));
                ref.invalidate(pendingClaimsProvider(userId));
              }
            }
            setState(() => _currentIndex = index);
          },
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

  Widget _buildDashboard(
    BuildContext context,
    String userId,
    UserState userState,
  ) {
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
          sliver: SliverToBoxAdapter(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLeaveBalanceCard(context, userId),
                const SizedBox(height: 16),

                _buildQuickStats(context, userId),
                const SizedBox(height: 24),

                Text(
                  "Quick Actions",
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ).animate().fadeIn(delay: 300.ms),
                const SizedBox(height: 12),
                _buildQuickActions(context),
              ],
            ),
          ),
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

  Widget _buildLeaveBalanceCard(BuildContext context, String userId) {
    final balanceAsync = ref.watch(leaveBalanceProvider(userId));

    return ShadCard(
          width: double.infinity,
          backgroundColor: Colors.black,
          border: ShadBorder.all(color: Colors.white24, width: 1),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    "Leave Balance",
                    style: GoogleFonts.playfairDisplay(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const Icon(Icons.beach_access, color: Colors.white, size: 20),
                ],
              ),
              const SizedBox(height: 16),
              balanceAsync.when(
                data: (data) {
                  final balances = (data['data'] as List?) ?? [];
                  if (balances.isEmpty) {
                    return const Text(
                      "No leave balance data",
                      style: TextStyle(color: Colors.grey),
                    );
                  }
                  return Column(
                    children: balances
                        .take(3)
                        .map(
                          (b) => _buildBalanceRow(
                            context,
                            b['leave_type_name'] ??
                                b['leave_type_id'] ??
                                'Leave',
                            b['total_days'] ?? 0,
                            b['used_days'] ?? 0,
                            b['pending_days'] ?? 0,
                          ),
                        )
                        .toList(),
                  );
                },
                loading: () => const Center(
                  child: SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  ),
                ),
                error: (e, _) => Center(
                  child: Text(
                    'Failed to load details',
                    style: TextStyle(color: Colors.red.shade300, fontSize: 12),
                  ),
                ),
              ),
            ],
          ),
        )
        .animate()
        .fadeIn(duration: 400.ms)
        .slideY(begin: 0.1, end: 0, curve: Curves.easeOutQuad);
  }

  Widget _buildBalanceRow(
    BuildContext context,
    String type,
    int total,
    int used,
    int pending,
  ) {
    final remaining = total - used - pending;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(type, style: TextStyle(color: Colors.grey[300])),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: remaining > 0
                      ? Colors.green.withValues(alpha: 0.2)
                      : Colors.red.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '$remaining / $total days',
                  style: TextStyle(
                    color: remaining > 0 ? Colors.green : Colors.redAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              if (pending > 0) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '$pending pending',
                    style: const TextStyle(color: Colors.orange, fontSize: 10),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context, String userId) {
    final leavesAsync = ref.watch(pendingLeavesProvider(userId));
    final claimsAsync = ref.watch(pendingClaimsProvider(userId));
    final bookingsAsync = ref.watch(pendingBookingsProvider(userId));

    return Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    context,
                    "Pending Leaves",
                    leavesAsync.when(
                      data: (d) => _countPending(d['data'] ?? []),
                      loading: () => "...",
                      error: (e, s) => "?",
                    ),
                    Icons.event_note,
                    Colors.purple,
                    onTap: () => _showPendingList(
                      context,
                      "Pending Leaves",
                      leavesAsync.value?['data'] ?? [],
                      "leave",
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    context,
                    "Pending Claims",
                    claimsAsync.when(
                      data: (d) => _countPending(d['data'] ?? []),
                      loading: () => "...",
                      error: (e, s) => "?",
                    ),
                    Icons.receipt_long,
                    Colors.orange,
                    onTap: () => _showPendingList(
                      context,
                      "Pending Claims",
                      claimsAsync.value?['data'] ?? [],
                      "claim",
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildStatCard(
              context,
              "Room Bookings",
              bookingsAsync.when(
                data: (d) => ((d['data'] as List?) ?? []).length.toString(),
                loading: () => "...",
                error: (e, s) => "?",
              ),
              Icons.meeting_room,
              Colors.teal,
              onTap: () => _showPendingList(
                context,
                "My Bookings",
                bookingsAsync.value?['data'] ?? [],
                "booking",
              ),
            ),
          ],
        )
        .animate()
        .fadeIn(delay: 100.ms, duration: 400.ms)
        .slideY(begin: 0.1, end: 0, curve: Curves.easeOutQuad);
  }

  String _countPending(List<dynamic> items) {
    final count = items.where((i) => i['status'] == 'pending').length;
    return count.toString();
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color, {
    VoidCallback? onTap,
  }) {
    return ShadCard(
      width: double.infinity,
      backgroundColor: Colors.black,
      border: ShadBorder.all(color: Colors.white24, width: 1),
      padding: const EdgeInsets.all(16),
      child: InkWell(
        onTap: onTap,
        child: Row(
          children: [
            Icon(icon, color: Colors.white, size: 24),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  title,
                  style: GoogleFonts.inter(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showPendingList(
    BuildContext context,
    String title,
    List<dynamic> items,
    String type,
  ) {
    final pendingItems = items.where((i) => i['status'] == 'pending').toList();

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E1E1E),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (pendingItems.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20),
                  child: Center(
                    child: Text(
                      "No pending items 🎉",
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                )
              else
                ConstrainedBox(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.of(context).size.height * 0.4,
                  ),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: pendingItems.length,
                    itemBuilder: (_, i) {
                      final item = pendingItems[i];
                      return _buildPendingItemTile(item, type);
                    },
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPendingItemTile(Map<String, dynamic> item, String type) {
    if (type == "leave") {
      final typeName = item['leave_type_name'] ?? 'Leave';
      final startDate = item['start_date'] ?? '';
      final endDate = item['end_date'] ?? '';
      final days = item['total_days'] ?? 1;

      return ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.purple.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.event_note, color: Colors.purple, size: 20),
        ),
        title: Text(typeName),
        subtitle: Text(
          "$startDate → $endDate ($days days)",
          style: TextStyle(color: Colors.grey[400], fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.orange.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Text(
            "PENDING",
            style: TextStyle(color: Colors.orange, fontSize: 10),
          ),
        ),
      );
    } else if (type == "claim") {
      final categoryName = item['category_name'] ?? 'Claim';
      final amount = item['amount'] ?? 0;
      final description = item['description'] ?? '';

      return ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.orange.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.receipt_long, color: Colors.orange, size: 20),
        ),
        title: Text(categoryName),
        subtitle: Text(
          "RM ${amount.toStringAsFixed(2)} - $description",
          style: TextStyle(color: Colors.grey[400], fontSize: 12),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.orange.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Text(
            "PENDING",
            style: TextStyle(color: Colors.orange, fontSize: 10),
          ),
        ),
      );
    } else if (type == "booking") {
      final roomName = item['room_name'] ?? 'Room';
      final title = item['title'] ?? 'Meeting';
      final startTime = item['start_time'] ?? '';
      final status = item['status'] ?? 'confirmed';

      return ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.teal.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.meeting_room, color: Colors.teal, size: 20),
        ),
        title: Text(roomName),
        subtitle: Text(
          "$title • ${startTime.toString().split('T').first}",
          style: TextStyle(color: Colors.grey[400], fontSize: 12),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.teal.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            status.toUpperCase(),
            style: const TextStyle(color: Colors.teal, fontSize: 10),
          ),
        ),
      );
    } else {
      return const SizedBox.shrink();
    }
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
                        () => _navigateToLeaveRequest(context),
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
                        () => _navigateToClaimSubmit(context),
                      )
                      .animate()
                      .fadeIn(delay: 350.ms, duration: 400.ms)
                      .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildActionButton(
              context,
              "Book Room",
              Icons.meeting_room,
              Colors.white,
              () => _navigateToRoomBooking(context),
            )
            .animate()
            .fadeIn(delay: 400.ms, duration: 400.ms)
            .slideY(begin: 0.2, end: 0, curve: Curves.easeOutQuad),
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

  void _navigateToLeaveRequest(BuildContext context) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const LeaveRequestScreen()),
    );

    if (result == true) {
      final userId = ref.read(userProvider).userId ?? '';
      ref.invalidate(leaveBalanceProvider(userId));
      ref.invalidate(pendingLeavesProvider(userId));
    }
  }

  void _navigateToClaimSubmit(BuildContext context) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const ClaimSubmitScreen()),
    );

    if (result == true) {
      final userId = ref.read(userProvider).userId ?? '';
      ref.invalidate(pendingClaimsProvider(userId));
    }
  }

  void _navigateToRoomBooking(BuildContext context) async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const RoomBookingScreen()),
    );
  }

  void _navigateToProfile(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ProfileScreen()),
    );
  }
}
