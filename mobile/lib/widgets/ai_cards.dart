/// ==============================================================================
/// MODULE: AI Cards (Generative UI)
/// ==============================================================================
///
/// Reusable UI widgets for AI-generated interactive cards.
/// These cards provide structured actions within the chat interface.
///
/// Includes:
/// - [LeaveConfirmationCard] - Leave request confirmation with Confirm/Cancel
/// ==============================================================================
library;

import 'package:flutter/material.dart';

class LeaveConfirmationCard extends StatelessWidget {
  final String date;
  final String type;
  final VoidCallback onConfirm;
  final VoidCallback onCancel;
  final bool isDisabled;

  const LeaveConfirmationCard({
    super.key,
    required this.date,
    required this.type,
    required this.onConfirm,
    required this.onCancel,
    this.isDisabled = false,
  });

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
                isDisabled ? Icons.check_circle : Icons.calendar_today,
                color: isDisabled ? Colors.green : Colors.orangeAccent,
              ),
              const SizedBox(width: 8),
              Text(
                isDisabled ? "Leave Submitted ✓" : "Leave Request",
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ],
          ),
          const Divider(color: Colors.grey),
          _row("Type", type),
          _row("Date", date),
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
                  "Action completed ✓",
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
                      backgroundColor: Theme.of(context).primaryColor,
                      foregroundColor: Colors.black,
                    ),
                    child: const Text("Confirm"),
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
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
