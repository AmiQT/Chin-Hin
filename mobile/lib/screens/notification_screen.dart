/// ==============================================================================
/// MODULE: Notification Screen
/// ==============================================================================
///
/// PURPOSE:
/// Displays a full history of all user notifications/nudges (read and unread).
/// Unlike the previous bottom sheet dialog, this screen persists notification
/// history even after marking them as read.
///
/// FEATURES:
/// - Pull-to-refresh to fetch latest nudges
/// - Visual distinction between read/unread notifications
/// - Mark as read functionality
/// - Type-based icons (claims, leaves, bookings, etc.)
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../providers/nudge_provider.dart';

class NotificationScreen extends ConsumerStatefulWidget {
  const NotificationScreen({super.key});

  @override
  ConsumerState<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends ConsumerState<NotificationScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(nudgeProvider.notifier).fetchAllNudges());
  }

  Future<void> _refresh() async {
    await ref.read(nudgeProvider.notifier).fetchAllNudges();
  }

  IconData _getIconForType(String? type) {
    switch (type) {
      case 'claim_reminder':
        return Icons.receipt_long;
      case 'leave_reminder':
        return Icons.beach_access;
      case 'booking_reminder':
        return Icons.meeting_room;
      default:
        return Icons.notifications;
    }
  }

  Color _getColorForType(String? type) {
    switch (type) {
      case 'claim_reminder':
        return Colors.green;
      case 'leave_reminder':
        return Colors.blue;
      case 'booking_reminder':
        return Colors.purple;
      default:
        return Colors.amber;
    }
  }

  @override
  Widget build(BuildContext context) {
    final nudges = ref.watch(nudgeProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Notifikasi',
          style: GoogleFonts.inter(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white70),
            onPressed: _refresh,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        color: Colors.amber,
        backgroundColor: Colors.grey[900],
        child: nudges.isEmpty
            ? _buildEmptyState()
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: nudges.length,
                itemBuilder: (context, index) {
                  final nudge = nudges[index];
                  return _buildNudgeCard(nudge);
                },
              ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.notifications_off_outlined,
            size: 80,
            color: Colors.grey[700],
          ),
          const SizedBox(height: 16),
          Text(
            'Tiada notifikasi',
            style: GoogleFonts.inter(color: Colors.grey[500], fontSize: 18),
          ),
          const SizedBox(height: 8),
          Text(
            'Tarik ke bawah untuk refresh',
            style: GoogleFonts.inter(color: Colors.grey[700], fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildNudgeCard(Map<String, dynamic> nudge) {
    final isRead = nudge['is_read'] == true;
    final type = nudge['type'] as String?;
    final createdAt = nudge['created_at'] != null
        ? DateTime.tryParse(nudge['created_at'])
        : null;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isRead ? Colors.grey[900] : Colors.grey[850],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isRead
              ? Colors.grey[800]!
              : Colors.amber.withValues(alpha: 0.5),
          width: isRead ? 1 : 2,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: _getColorForType(type).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                _getIconForType(type),
                color: _getColorForType(type),
                size: 24,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          nudge['title'] ?? 'Notifikasi',
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontWeight: isRead
                                ? FontWeight.normal
                                : FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                      ),
                      if (!isRead)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.amber,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            'BARU',
                            style: GoogleFonts.inter(
                              color: Colors.black,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    nudge['content'] ?? '',
                    style: GoogleFonts.inter(
                      color: isRead ? Colors.grey[500] : Colors.grey[300],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (createdAt != null)
                        Text(
                          DateFormat('dd MMM, HH:mm').format(createdAt),
                          style: GoogleFonts.inter(
                            color: Colors.grey[600],
                            fontSize: 11,
                          ),
                        ),
                      if (!isRead)
                        GestureDetector(
                          onTap: () {
                            ref
                                .read(nudgeProvider.notifier)
                                .markAsRead(nudge['id']);
                          },
                          child: Row(
                            children: [
                              Icon(
                                Icons.check_circle_outline,
                                color: Colors.green[400],
                                size: 16,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Tandakan dibaca',
                                style: GoogleFonts.inter(
                                  color: Colors.green[400],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
