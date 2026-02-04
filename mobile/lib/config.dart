/// ==============================================================================
/// MODULE: Config
/// ==============================================================================
///
/// Environment configuration for API base URL.
/// Automatically detects platform and sets appropriate localhost address.
/// ==============================================================================
library;

import 'dart:io';

class Config {
  static String get baseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  static const String testUserId = "11111111-1111-1111-1111-111111111111";
}
