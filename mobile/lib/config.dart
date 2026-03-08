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
  static bool get isLocal => true;

  static String get baseUrl {
    if (isLocal) {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000';
      }
      return 'http://localhost:8000';
    }
    // Production URL (Cloudflare Tunnel)
    return 'https://nato-provides-michigan-trend.trycloudflare.com';
  }

  static const String testUserId = "11111111-1111-1111-1111-111111111111";
}
