/// ==============================================================================
/// MODULE: Avatar Selector Widget
/// ==============================================================================
///
/// A bottom sheet widget to select from pre-made 3D cartoon avatars.
/// Returns selected avatar ID for profile customization.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// List of available avatar asset paths
const List<String> avatarAssets = [
  'assets/avatars/avatar_1.png',
  'assets/avatars/avatar_2.png',
  'assets/avatars/avatar_3.png',
  'assets/avatars/avatar_4.png',
  'assets/avatars/avatar_5.png',
];

/// Shows avatar selection dialog and returns selected avatar ID
Future<String?> showAvatarSelector(
  BuildContext context, {
  String? currentAvatarId,
}) {
  return showModalBottomSheet<String>(
    context: context,
    backgroundColor: Colors.black,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      side: BorderSide(color: Colors.white24),
    ),
    builder: (ctx) => _AvatarSelectorSheet(currentAvatarId: currentAvatarId),
  );
}

class _AvatarSelectorSheet extends StatelessWidget {
  final String? currentAvatarId;

  const _AvatarSelectorSheet({this.currentAvatarId});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.white30,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            "Choose Your Avatar",
            style: GoogleFonts.playfairDisplay(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Select a profile picture that represents you",
            style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 14),
          ),
          const SizedBox(height: 24),
          SizedBox(
            height: 120,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: avatarAssets.length,
              itemBuilder: (ctx, index) {
                final avatarId = 'avatar_${index + 1}';
                final isSelected = currentAvatarId == avatarId;

                return GestureDetector(
                  onTap: () => Navigator.pop(context, avatarId),
                  child: Container(
                    width: 100,
                    height: 100,
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: isSelected ? Colors.white : Colors.white24,
                        width: isSelected ? 3 : 1,
                      ),
                    ),
                    child: ClipOval(
                      child: Image.asset(
                        avatarAssets[index],
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

/// Widget to display avatar or initials fallback
class AvatarDisplay extends StatelessWidget {
  final String? avatarId;
  final String? fallbackName;
  final double size;
  final VoidCallback? onTap;

  const AvatarDisplay({
    super.key,
    this.avatarId,
    this.fallbackName,
    this.size = 80,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.black,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: avatarId != null && avatarId!.startsWith('avatar_')
                ? ClipOval(
                    child: Image.asset(
                      'assets/avatars/$avatarId.png',
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) =>
                          _buildInitials(),
                    ),
                  )
                : _buildInitials(),
          ),
          if (onTap != null)
            Positioned(
              bottom: 0,
              right: 0,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.black, width: 2),
                ),
                child: const Icon(Icons.edit, size: 14, color: Colors.black),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInitials() {
    final initials = _getInitials(fallbackName ?? 'U');
    return Center(
      child: Text(
        initials,
        style: GoogleFonts.playfairDisplay(
          fontSize: size * 0.35,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    );
  }

  String _getInitials(String name) {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : 'U';
  }
}
