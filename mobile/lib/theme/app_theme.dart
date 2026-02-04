/// ==============================================================================
/// MODULE: App Theme
/// ==============================================================================
///
/// Corporate Noir design system for the Chin Hin Employee Assistant.
/// Defines ShadCN and Material theme configurations with dark mode aesthetics.
///
/// Uses Playfair Display for headings and Inter for body text.
/// ==============================================================================
library;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

class AppTheme {
  static final shadDarkTheme = ShadThemeData(
    brightness: Brightness.dark,
    colorScheme: const ShadColorScheme(
      background: Colors.black,
      foreground: Colors.white,
      primary: Colors.white,
      primaryForeground: Colors.black,
      popover: Colors.black,
      popoverForeground: Colors.white,
      card: Colors.black,
      cardForeground: Colors.white,
      border: Colors.white24,
      input: Colors.white24,
      ring: Colors.white, // Focus ring
      secondary: Colors.white10,
      secondaryForeground: Colors.white,
      muted: Colors.white10,
      mutedForeground: Colors.grey,
      accent: Colors.white10,
      accentForeground: Colors.white,
      destructive: Colors.red,
      destructiveForeground: Colors.white,
      selection: Colors.white24,
    ),
    radius: const BorderRadius.all(Radius.circular(2)), // Sharp-ish corners
    textTheme: ShadTextTheme(
      family: GoogleFonts.inter().fontFamily!,
      large: GoogleFonts.playfairDisplay(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: Colors.white,
      ),
      h1Large: GoogleFonts.playfairDisplay(
        fontSize: 36,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
      p: GoogleFonts.inter(fontSize: 14, color: Colors.white),
    ),
  );
  static final darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: const Color(0xFF121212),
    primaryColor: const Color(0xFF00E5FF), // Cyan Accent
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF00E5FF),
      secondary: Color(0xFFFF4081),
      surface: Color(0xFF1E1E1E),
      onPrimary: Colors.black,
    ),
    textTheme: GoogleFonts.interTextTheme(
      ThemeData.dark().textTheme,
    ).apply(bodyColor: Colors.white, displayColor: Colors.white),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
    ),
  );
}
