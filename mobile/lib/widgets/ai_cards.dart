/// ==============================================================================
/// MODULE: AI Cards (Generative UI)
/// ==============================================================================
///
/// Reusable UI widgets for AI-generated interactive cards.
/// These cards provide structured, interactive actions within the chat interface.
///
/// Cards:
/// - [ActionConfirmationCard] - HITL confirmation for sensitive actions (Leave/Room/Transport)
/// - [LeaveBalanceCard]       - Leave balances with quick-tap apply shortcuts
/// - [VehiclePickerCard]      - Tap-to-select vehicle type for transport booking
/// - [MenuCard]               - Styled daily cafe menu display
/// - [EnergyCard]             - Monthly energy consumption with stats comparison
/// - [ClaimsCard]             - Expense claims list with status badges
/// - [QuickRepliesRow]        - Horizontal scrollable suggestion chips
/// - [DatePickerBar]          - Inline date picker shortcut when AI asks for a date
/// ==============================================================================
library;

import 'package:flutter/material.dart';

class ActionConfirmationCard extends StatelessWidget {
  final String tool;
  final Map<String, dynamic> args;
  final VoidCallback onConfirm;
  final VoidCallback onCancel;
  final bool isDisabled;

  const ActionConfirmationCard({
    super.key,
    required this.tool,
    required this.args,
    required this.onConfirm,
    required this.onCancel,
    this.isDisabled = false,
  });

  String get _title {
    switch (tool) {
      case 'apply_leave':
        return 'Leave Request 🏖️';
      case 'book_room':
        return 'Room Booking 🏢';
      case 'book_transport':
        return 'Transport Request 🚐';
      default:
        return 'Confirmation';
    }
  }

  IconData get _icon {
    switch (tool) {
      case 'apply_leave':
        return Icons.beach_access;
      case 'book_room':
        return Icons.meeting_room;
      case 'book_transport':
        return Icons.directions_car;
      default:
        return Icons.check_circle_outline;
    }
  }

  List<Map<String, String>> get _details {
    switch (tool) {
      case 'apply_leave':
        return [
          {
            'label': 'Jenis Cuti',
            'value': args['leave_type']?.toString() ?? 'N/A',
          },
          {
            'label': 'Tarikh Mula',
            'value': args['start_date']?.toString() ?? 'N/A',
          },
          {
            'label': 'Tarikh Akhir',
            'value': args['end_date']?.toString() ?? 'N/A',
          },
          {'label': 'Sebab', 'value': args['reason']?.toString() ?? 'N/A'},
        ];
      case 'book_room':
        return [
          {'label': 'Bilik', 'value': args['room_name']?.toString() ?? 'N/A'},
          {'label': 'Tarikh', 'value': args['date']?.toString() ?? 'N/A'},
          {
            'label': 'Masa Mula',
            'value': args['start_time']?.toString() ?? 'N/A',
          },
          {
            'label': 'Masa Tamat',
            'value': args['end_time']?.toString() ?? 'N/A',
          },
          {'label': 'Tujuan', 'value': args['purpose']?.toString() ?? 'N/A'},
        ];
      case 'book_transport':
        return [
          {
            'label': 'Kenderaan',
            'value': args['vehicle_type']?.toString() ?? 'N/A',
          },
          {
            'label': 'Destinasi',
            'value': args['destination']?.toString() ?? 'N/A',
          },
          {'label': 'Tarikh', 'value': args['date']?.toString() ?? 'N/A'},
          {'label': 'Masa', 'value': args['time']?.toString() ?? 'N/A'},
          {'label': 'Sebab', 'value': args['reason']?.toString() ?? 'N/A'},
        ];
      default:
        return args.entries
            .map((e) => {'label': e.key, 'value': e.value.toString()})
            .toList();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF2C2C2C),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isDisabled ? Icons.check_circle : _icon,
                color: isDisabled ? Colors.green : Colors.orangeAccent,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  isDisabled ? "$_title — Done ✓" : _title,
                  style: Theme.of(context).textTheme.titleMedium,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const Divider(color: Colors.grey),
          ..._details.map((d) => _row(d['label']!, d['value']!)),
          const SizedBox(height: 16),
          if (isDisabled)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Text(
                  "Dah selesai ✓",
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            )
          else
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: onCancel,
                    child: const Text("Cancel"),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: onConfirm,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      "Confirm",
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// SHARED HELPERS
// ─────────────────────────────────────────────────────────

Widget _cardShell({required Widget child, Color? accent}) {
  return Container(
    margin: const EdgeInsets.only(top: 8),
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: const Color(0xFF1E1E1E),
      borderRadius: BorderRadius.circular(16),
      border: Border.all(
        color: (accent ?? Colors.white).withValues(alpha: 0.15),
        width: 1,
      ),
    ),
    child: child,
  );
}

Widget _cardHeader(String title, IconData icon, Color color) {
  return Row(
    children: [
      Icon(icon, color: color, size: 20),
      const SizedBox(width: 8),
      Text(
        title,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 15,
        ),
      ),
    ],
  );
}

// ─────────────────────────────────────────────────────────
// LeaveBalanceCard — Baki cuti + quick reply chips
// ─────────────────────────────────────────────────────────

class LeaveBalanceCard extends StatelessWidget {
  final Map<String, dynamic> balances;
  final List<String> quickReplies;
  final Function(String) onQuickReply;

  const LeaveBalanceCard({
    super.key,
    required this.balances,
    required this.quickReplies,
    required this.onQuickReply,
  });

  static const _leaveColors = {
    'Annual': Color(0xFF4FC3F7),
    'Medical': Color(0xFF81C784),
    'Emergency': Color(0xFFFF8A65),
  };

  static const _leaveMax = {'Annual': 12, 'Medical': 14, 'Emergency': 5};

  static const _leaveIcons = {
    'Annual': Icons.beach_access,
    'Medical': Icons.local_hospital,
    'Emergency': Icons.warning_amber_rounded,
  };

  @override
  Widget build(BuildContext context) {
    return _cardShell(
      accent: const Color(0xFF4FC3F7),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader(
            'Baki Cuti Kau 🏖️',
            Icons.calendar_today,
            const Color(0xFF4FC3F7),
          ),
          const Divider(color: Colors.white12, height: 20),
          ...balances.entries.map((entry) {
            final type = entry.key;
            final remaining = (entry.value as num).toInt();
            final max = _leaveMax[type] ?? 14;
            final used = max - remaining;
            final color = _leaveColors[type] ?? Colors.white54;
            final icon = _leaveIcons[type] ?? Icons.event;

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(icon, color: color, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        type,
                        style: TextStyle(
                          color: color,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '$remaining / $max hari',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: used / max,
                      backgroundColor: Colors.white12,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        color.withValues(alpha: 0.7),
                      ),
                      minHeight: 6,
                    ),
                  ),
                ],
              ),
            );
          }),
          if (quickReplies.isNotEmpty) ...[
            const Divider(color: Colors.white12, height: 20),
            const Text(
              'Apply cuti sekarang:',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 8),
            QuickRepliesRow(replies: quickReplies, onTap: onQuickReply),
          ],
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// VehiclePickerCard — Tap pilih kenderaan
// ─────────────────────────────────────────────────────────

class VehiclePickerCard extends StatelessWidget {
  final List<Map<String, dynamic>> vehicles;
  final Function(String vehicleType) onSelect;
  final bool isDisabled;

  const VehiclePickerCard({
    super.key,
    required this.vehicles,
    required this.onSelect,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context) {
    return _cardShell(
      accent: Colors.blueAccent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader(
            isDisabled ? 'Kenderaan Dipilih ✓' : 'Pilih Kenderaan 🚐',
            Icons.directions_car,
            Colors.blueAccent,
          ),
          const Divider(color: Colors.white12, height: 20),
          if (isDisabled)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Text(
                  'Pilihan dah sent ✓',
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            )
          else
            Row(
              children: vehicles.map((v) {
                final type = v['type'] as String;
                final capacity = v['capacity'] as String;
                final emoji = v['emoji'] as String? ?? '🚗';
                return Expanded(
                  child: GestureDetector(
                    onTap: () => onSelect(type),
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.05),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.blueAccent.withValues(alpha: 0.4),
                        ),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(emoji, style: const TextStyle(fontSize: 28)),
                          const SizedBox(height: 6),
                          Text(
                            type,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            capacity,
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          if (!isDisabled) ...[
            const SizedBox(height: 10),
            const Center(
              child: Text(
                'Tap untuk pilih kenderaan kau',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// MenuCard — Menu cafe hari ni
// ─────────────────────────────────────────────────────────

class MenuCard extends StatelessWidget {
  final String day;
  final String menu;

  const MenuCard({super.key, required this.day, required this.menu});

  @override
  Widget build(BuildContext context) {
    return _cardShell(
      accent: Colors.orangeAccent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader(
            'Menu Cafe Harini 🍛',
            Icons.restaurant,
            Colors.orangeAccent,
          ),
          const Divider(color: Colors.white12, height: 20),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.orangeAccent.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: Colors.orangeAccent.withValues(alpha: 0.2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  day.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.orangeAccent,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  menu,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            '⏰ Cafe buka 12:00pm – 2:00pm',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// EnergyCard — Usage elektrik bulanan
// ─────────────────────────────────────────────────────────

class EnergyCard extends StatelessWidget {
  final String currentMonth;
  final int currentUsage;
  final Map<String, dynamic> allStats;

  const EnergyCard({
    super.key,
    required this.currentMonth,
    required this.currentUsage,
    required this.allStats,
  });

  @override
  Widget build(BuildContext context) {
    final maxUsage = allStats.values.whereType<int>().fold(
      0,
      (a, b) => a > b ? a : b,
    );

    final months = allStats.keys.toList();
    final currentIdx = months.indexOf(currentMonth);
    final prevMonth = currentIdx > 0 ? months[currentIdx - 1] : null;
    final prevUsage = prevMonth != null ? allStats[prevMonth] as int? : null;

    final isImproving = prevUsage != null && currentUsage < prevUsage;
    final diffPercent = prevUsage != null && prevUsage > 0
        ? (((prevUsage - currentUsage) / prevUsage) * 100)
              .abs()
              .toStringAsFixed(1)
        : null;

    return _cardShell(
      accent: Colors.greenAccent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Energy Consumption ⚡', Icons.bolt, Colors.greenAccent),
          const Divider(color: Colors.white12, height: 20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '$currentUsage',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 6),
              const Padding(
                padding: EdgeInsets.only(bottom: 6),
                child: Text(
                  'kWh',
                  style: TextStyle(color: Colors.grey, fontSize: 14),
                ),
              ),
              const Spacer(),
              if (prevUsage != null && diffPercent != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: isImproving
                        ? Colors.green.withValues(alpha: 0.15)
                        : Colors.red.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    isImproving ? '▼ $diffPercent%' : '▲ $diffPercent%',
                    style: TextStyle(
                      color: isImproving
                          ? Colors.greenAccent
                          : Colors.redAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                ),
            ],
          ),
          Text(
            currentMonth,
            style: const TextStyle(color: Colors.grey, fontSize: 13),
          ),
          const SizedBox(height: 16),
          ...allStats.entries.map((entry) {
            final month = entry.key;
            final usage = (entry.value as num).toInt();
            final ratio = maxUsage > 0 ? usage / maxUsage : 0.0;
            final isCurrentMonth = month == currentMonth;

            return Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                children: [
                  SizedBox(
                    width: 70,
                    child: Text(
                      month.substring(0, 3).toUpperCase(),
                      style: TextStyle(
                        color: isCurrentMonth
                            ? Colors.greenAccent
                            : Colors.grey,
                        fontSize: 11,
                        fontWeight: isCurrentMonth
                            ? FontWeight.bold
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: ratio,
                        backgroundColor: Colors.white10,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          isCurrentMonth ? Colors.greenAccent : Colors.white24,
                        ),
                        minHeight: 8,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 50,
                    child: Text(
                      '$usage',
                      textAlign: TextAlign.right,
                      style: TextStyle(
                        color: isCurrentMonth ? Colors.white : Colors.grey,
                        fontSize: 11,
                        fontWeight: isCurrentMonth
                            ? FontWeight.bold
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
          const Divider(color: Colors.white12, height: 20),
          const Text(
            '💡 Tip: Matikan aircond bila keluar lunch. Boleh jimat ~5% sebulan!',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// ClaimsCard — Status expense claims
// ─────────────────────────────────────────────────────────

class ClaimsCard extends StatelessWidget {
  final List<dynamic> claims;

  const ClaimsCard({super.key, required this.claims});

  @override
  Widget build(BuildContext context) {
    return _cardShell(
      accent: Colors.purpleAccent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader(
            'Expense Claims 💸',
            Icons.receipt_long,
            Colors.purpleAccent,
          ),
          const Divider(color: Colors.white12, height: 20),
          if (claims.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text(
                  'Takde claim pending. Semua clear! ✅',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            )
          else
            ...claims.map((c) {
              final claim = c as Map<String, dynamic>;
              final status = claim['status'] as String? ?? 'unknown';
              final isPending = status == 'pending';
              final isApproved = status == 'approved';

              final statusColor = isPending
                  ? Colors.orangeAccent
                  : isApproved
                  ? Colors.greenAccent
                  : Colors.grey;

              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.03),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.white12),
                ),
                child: Row(
                  children: [
                    Icon(
                      isPending
                          ? Icons.hourglass_top
                          : Icons.check_circle_outline,
                      color: statusColor,
                      size: 18,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            claim['type']?.toString() ?? 'Claim',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                              fontSize: 13,
                            ),
                          ),
                          Text(
                            'RM ${claim['amount']?.toString() ?? '0'}',
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        status.toUpperCase(),
                        style: TextStyle(
                          color: statusColor,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// QuickRepliesRow — Suggestion chips horizontal scroll
// ─────────────────────────────────────────────────────────

class QuickRepliesRow extends StatelessWidget {
  final List<String> replies;
  final Function(String) onTap;

  const QuickRepliesRow({
    super.key,
    required this.replies,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: replies.map((reply) {
          return GestureDetector(
            onTap: () => onTap(reply),
            child: Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.07),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white24),
              ),
              child: Text(
                reply,
                style: const TextStyle(color: Colors.white, fontSize: 13),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// DatePickerBar — Shortcut date picker bila AI tanya tarikh
// ─────────────────────────────────────────────────────────

class DatePickerBar extends StatelessWidget {
  /// Called with the picked date formatted as YYYY-MM-DD.
  final Function(String formattedDate) onDatePicked;

  const DatePickerBar({super.key, required this.onDatePicked});

  Future<void> _openPicker(BuildContext context) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 2),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.dark(
              primary: Colors.white,
              onPrimary: Colors.black,
              surface: Color(0xFF1E1E1E),
              onSurface: Colors.white,
            ),
            dialogTheme: const DialogThemeData(
              backgroundColor: Color(0xFF1E1E1E),
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      final formatted =
          '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      onDatePicked(formatted);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 6, bottom: 4),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => _openPicker(context),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white30),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.calendar_month_rounded,
                    color: Colors.white70,
                    size: 16,
                  ),
                  SizedBox(width: 6),
                  Text(
                    'Pilih Tarikh 📅',
                    style: TextStyle(color: Colors.white, fontSize: 13),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          const Text(
            'atau taip je ↓',
            style: TextStyle(color: Colors.white38, fontSize: 11),
          ),
        ],
      ),
    );
  }
}
