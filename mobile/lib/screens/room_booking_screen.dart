/// ==============================================================================
/// MODULE: Room Booking Screen
/// ==============================================================================
///
/// Meeting room reservation form for employees. Allows users to:
/// - Select available room with capacity info
/// - Pick date and time slot
/// - Add meeting title and optional description
/// - Submit booking request
///
/// Uses [roomsProvider] to fetch available rooms.
/// On successful booking, returns `true` to trigger list refresh.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';
import '../providers/chat_provider.dart';

final roomsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiService = ref.read(apiServiceProvider);
  return await apiService.getRooms();
});

class RoomBookingScreen extends ConsumerStatefulWidget {
  const RoomBookingScreen({super.key});

  @override
  ConsumerState<RoomBookingScreen> createState() => _RoomBookingScreenState();
}

class _RoomBookingScreenState extends ConsumerState<RoomBookingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  String? _selectedRoomId;
  String? _selectedRoomName;
  int? _selectedRoomCapacity;
  DateTime? _selectedDate;
  TimeOfDay? _startTime;
  TimeOfDay? _endTime;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 60)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.dark(
              primary: Colors.purple,
              surface: const Color(0xFF1E1E1E),
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _selectTime(BuildContext context, bool isStartTime) async {
    final initialTime = isStartTime
        ? (_startTime ?? const TimeOfDay(hour: 9, minute: 0))
        : (_endTime ?? TimeOfDay(hour: (_startTime?.hour ?? 9) + 1, minute: 0));

    final picked = await showTimePicker(
      context: context,
      initialTime: initialTime,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.dark(
              primary: Colors.purple,
              surface: const Color(0xFF1E1E1E),
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() {
        if (isStartTime) {
          _startTime = picked;
          if (_endTime == null ||
              _timeToMinutes(_endTime!) <= _timeToMinutes(picked)) {
            _endTime = TimeOfDay(hour: picked.hour + 1, minute: picked.minute);
          }
        } else {
          _endTime = picked;
        }
      });
    }
  }

  int _timeToMinutes(TimeOfDay time) => time.hour * 60 + time.minute;

  String get _duration {
    if (_startTime == null || _endTime == null) return '';
    final startMinutes = _timeToMinutes(_startTime!);
    final endMinutes = _timeToMinutes(_endTime!);
    final diff = endMinutes - startMinutes;
    if (diff <= 0) return 'Invalid';
    final hours = diff ~/ 60;
    final mins = diff % 60;
    if (hours > 0 && mins > 0) return '${hours}h ${mins}m';
    if (hours > 0) return '${hours}h';
    return '${mins}m';
  }

  Future<void> _submitBooking() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedRoomId == null ||
        _selectedDate == null ||
        _startTime == null ||
        _endTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all required fields')),
      );
      return;
    }

    if (_timeToMinutes(_endTime!) <= _timeToMinutes(_startTime!)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('End time must be after start time')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final userId = ref.read(userProvider).userId!;
      final apiService = ref.read(apiServiceProvider);

      final startDateTime = DateTime(
        _selectedDate!.year,
        _selectedDate!.month,
        _selectedDate!.day,
        _startTime!.hour,
        _startTime!.minute,
      );
      final endDateTime = DateTime(
        _selectedDate!.year,
        _selectedDate!.month,
        _selectedDate!.day,
        _endTime!.hour,
        _endTime!.minute,
      );

      final result = await apiService.bookRoom(
        userId: userId,
        roomId: _selectedRoomId!,
        title: _titleController.text.trim(),
        startTime: startDateTime.toIso8601String(),
        endTime: endDateTime.toIso8601String(),
        description: _descriptionController.text.trim().isNotEmpty
            ? _descriptionController.text.trim()
            : null,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message'] ??
                  '$_selectedRoomName booked! (Capacity: $_selectedRoomCapacity) 🏢',
            ),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final roomsAsync = ref.watch(roomsProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(
          "Book Meeting Room",
          style: GoogleFonts.playfairDisplay(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ShadCard(
                width: double.infinity,
                backgroundColor: Colors.white10,
                border: ShadBorder.all(color: Colors.white24, width: 1),
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(
                      Icons.meeting_room,
                      color: Colors.white,
                      size: 40,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Book a Room",
                            style: GoogleFonts.playfairDisplay(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            "Reserve a meeting space",
                            style: GoogleFonts.inter(color: Colors.grey[400]),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn().slideY(begin: 0.2, end: 0),

              const SizedBox(height: 24),

              Text(
                "Select Room *",
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              roomsAsync.when(
                data: (data) {
                  final rooms = (data['data'] as List?) ?? [];
                  return Column(
                    children: rooms.map<Widget>((room) {
                      final isSelected =
                          _selectedRoomId == room['id'].toString();
                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedRoomId = room['id'].toString();
                            _selectedRoomName = room['name'];
                            _selectedRoomCapacity = room['capacity'];
                          });
                        },
                        child: Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: isSelected ? Colors.white10 : Colors.black,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isSelected ? Colors.white : Colors.white24,
                              width: isSelected ? 1 : 1,
                            ),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.meeting_room,
                                color: isSelected ? Colors.white : Colors.grey,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      room['name'] ?? 'Room',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: isSelected
                                            ? Colors.white
                                            : Colors.grey[300],
                                      ),
                                    ),
                                    if (room['location'] != null)
                                      Text(
                                        room['location'],
                                        style: TextStyle(
                                          color: Colors.grey[500],
                                          fontSize: 12,
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white10,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(
                                      Icons.people,
                                      size: 14,
                                      color: Colors.white,
                                    ),
                                    const SizedBox(width: 4),
                                    Text(
                                      '${room['capacity'] ?? '?'}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              if (isSelected) ...[
                                const SizedBox(width: 8),
                                const Icon(
                                  Icons.check_circle,
                                  color: Colors.white,
                                ),
                              ],
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Text(
                  'Failed to load: $e',
                  style: const TextStyle(color: Colors.redAccent),
                ),
              ),

              const SizedBox(height: 20),

              Text(
                "Meeting Title *",
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              ShadInput(
                controller: _titleController,
                placeholder: const Text("e.g., Sprint Planning, Team Sync"),
              ).animate().fadeIn(delay: 100.ms),

              const SizedBox(height: 20),

              Text(
                "Date *",
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              InkWell(
                onTap: () => _selectDate(context),
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white10,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white24),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.calendar_today, size: 18, color: Colors.white),
                      const SizedBox(width: 12),
                      Text(
                        _selectedDate != null
                            ? DateFormat(
                                'EEEE, dd MMM yyyy',
                              ).format(_selectedDate!)
                            : "Select date",
                        style: TextStyle(
                          color: _selectedDate != null
                              ? Colors.white
                              : Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ).animate().fadeIn(delay: 150.ms),

              const SizedBox(height: 20),

              Row(
                children: [
                  Expanded(
                    child: _buildTimeField(
                      context,
                      "Start Time *",
                      _startTime,
                      () => _selectTime(context, true),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTimeField(
                      context,
                      "End Time *",
                      _endTime,
                      () => _selectTime(context, false),
                    ),
                  ),
                ],
              ).animate().fadeIn(delay: 200.ms),

              if (_duration.isNotEmpty && _duration != 'Invalid')
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white10,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.timer, size: 16, color: Colors.white),
                        const SizedBox(width: 8),
                        Text(
                          "Duration: $_duration",
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn().scale(),
                ),

              const SizedBox(height: 20),

              Text(
                "Description (Optional)",
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              ShadInput(
                controller: _descriptionController,
                maxLines: 2,
                placeholder: const Text("Agenda, attendees, etc."),
              ).animate().fadeIn(delay: 250.ms),

              const SizedBox(height: 32),

              ShadButton(
                width: double.infinity,
                onPressed: _isSubmitting ? null : _submitBooking,
                child: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.black,
                        ),
                      )
                    : Text(
                        "Book Room",
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
              ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTimeField(
    BuildContext context,
    String label,
    TimeOfDay? time,
    VoidCallback onTap,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(color: Colors.grey[400], fontSize: 14)),
        const SizedBox(height: 8),
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            decoration: BoxDecoration(
              color: Colors.white10,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white24),
            ),
            child: Row(
              children: [
                Icon(Icons.access_time, size: 18, color: Colors.white),
                const SizedBox(width: 12),
                Text(
                  time != null ? time.format(context) : "Select",
                  style: TextStyle(
                    color: time != null ? Colors.white : Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
