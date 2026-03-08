# 📱 Chin Hin Employee AI Assistant - Mobile App

> Flutter-based mobile interface for AI-powered employee services

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Flutter 3.x |
| State | Riverpod 2.0 (Notifier Pattern) |
| UI Library | ShadCN UI |
| HTTP Client | Dio |
| Auth | Simple Token Auth (SharedPreferences) |
| Voice | Speech-to-Text |
| Camera | Camera + Record packages |

## 📂 Project Structure

```
lib/
├── main.dart              # App entry point
├── config.dart            # API URL configuration
├── core/
│   └── app_config.dart
├── models/
│   └── message.dart       # Chat message model
├── providers/
│   ├── user_provider.dart # Auth state
│   ├── chat_provider.dart # Chat state
│   └── nudge_provider.dart # Notifications
├── screens/
│   ├── login_screen.dart
│   ├── home_screen.dart   # Dashboard + Navigation
│   ├── chat_screen.dart   # AI chat interface
│   ├── profile_screen.dart
│   ├── leave_request_screen.dart
│   ├── claim_submit_screen.dart
│   ├── room_booking_screen.dart
│   └── live_vision_screen.dart # Gemini Live Vision
├── services/
│   ├── api_service.dart   # HTTP wrapper
│   └── live_vision_service.dart # WebSocket for vision
├── theme/
│   └── app_theme.dart     # Corporate Noir theme
└── widgets/
    └── ai_cards.dart      # Generative UI cards
```

## 🚀 Quick Start

```bash
cd mobile
flutter pub get
flutter run
```

## ✨ Key Features

- **AI Chat** - Multimodal chat with text, voice & images
- **Live Vision** - Real-time camera/audio streaming to Gemini
- **Leave Management** - Apply & track leave requests
- **Expense Claims** - Submit claims with receipt photos
- **Room Booking** - Book meeting rooms
- **Proactive Nudges** - AI-generated reminders

## ⚙️ Configuration

Edit `lib/config.dart` for API URL:
- Android Emulator: `http://10.0.2.2:8000`
- iOS Simulator: `http://localhost:8000`
- Physical Device: Use PC's LAN IP

---
*Built with ❤️ for Chin Hin*
