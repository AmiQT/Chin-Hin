# 📱 Chin Hin Employee AI - Mobile App Documentation

> **Role**: Frontend Interface (Flutter)  
> **Status**: Production Ready  
> **Last Updated**: 02 Feb 2026

---

## 🏗️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Flutter 3.x | Cross-platform mobile UI |
| **Language** | Dart | Programming logic |
| **State Management** | Riverpod 2.0 | Reactive state & dependency injection |
| **UI Library** | ShadCN UI | Modern component system |
| **Networking** | Dio | HTTP requests to Backend API |
| **Auth** | Supabase Auth | JWT-based authentication |
| **Styling** | Google Fonts + Flutter Animate | Typography & animations |
| **Voice** | Speech-to-Text | Voice command input |
| **Camera** | Camera + Record | Live Vision feature |
| **Markdown** | Flutter Markdown | Rich text rendering |

---

## 📂 Project Structure (`/mobile`)

```text
lib/
├── main.dart              # Entry point & app initialization
├── config.dart            # API URL configuration
├── core/
│   └── supabase_config.dart # Supabase credentials
├── models/
│   └── message.dart       # Chat message data model
├── providers/
│   ├── user_provider.dart # Authentication state
│   ├── chat_provider.dart # Chat state & API calls
│   └── nudge_provider.dart # Proactive notifications
├── screens/
│   ├── login_screen.dart  # Email/password auth
│   ├── home_screen.dart   # Dashboard + bottom nav
│   ├── chat_screen.dart   # AI chat (Action Island)
│   ├── profile_screen.dart # User profile & stats
│   ├── leave_request_screen.dart # Leave application
│   ├── claim_submit_screen.dart  # Expense submission
│   ├── room_booking_screen.dart  # Room reservations
│   └── live_vision_screen.dart   # Gemini Live Vision
├── services/
│   ├── api_service.dart   # Dio HTTP wrapper
│   └── live_vision_service.dart # WebSocket for vision
├── theme/
│   └── app_theme.dart     # Corporate Noir dark theme
└── widgets/
    └── ai_cards.dart      # Generative UI components
```

---

## ✨ Key Features

### 1. 🔐 Supabase Authentication
- Email/password sign-up and sign-in
- JWT token auto-attached to all API requests
- Persistent session with auto-login

### 2. 🧠 AI Chat Interface
- **Action Island UI**: Floating input bar design
- **Multimodal**: Text, voice input, image attachments
- **Markdown Support**: Rich text rendering for AI responses
- **Generative UI**: Smart widgets (LeaveConfirmationCard)

### 3. 🎤 Voice Input
- Native microphone integration
- Tap mic icon to start/stop listening
- Auto-fills text in input bar

### 4. 👁️ Live Vision (Gemini 2.0)
- Real-time camera streaming via WebSocket
- Audio capture and streaming
- Ephemeral token authentication
- Live transcript display

### 5. 📋 Employee Services
- **Leave Management**: Apply, view balance, track requests
- **Expense Claims**: Submit with receipt photos
- **Room Booking**: Reserve meeting rooms
- **Profile**: View stats and quick actions

### 6. 🔔 Proactive Nudges
- AI-generated reminders
- Badge notification in chat header
- Mark as read functionality

---

## 🔌 API Integration

The app connects to the Python backend via `ApiService`.

- **Base URL**: Defined in `lib/config.dart`
    - Android Emulator: `http://10.0.2.2:8000`
    - iOS Simulator: `http://localhost:8000`
    - Physical Device: PC's LAN IP (e.g., `192.168.x.x`)

### Endpoints Used

| Category | Endpoints |
|----------|-----------|
| Chat | `POST /api/v1/chat` |
| Nudges | `GET /api/v1/nudges`, `POST /api/v1/nudges/:id/read` |
| Leaves | `GET /api/v1/leaves/balance`, `POST /api/v1/leaves` |
| Claims | `GET /api/v1/claims/categories`, `POST /api/v1/claims` |
| Rooms | `GET /api/v1/rooms`, `POST /api/v1/rooms/book` |
| Live Vision | `GET /api/v1/live-vision/token` |

---

## 🚀 Setup & Run Guide

### Prerequisites
- Flutter SDK installed
- Android Studio / VS Code with Flutter extensions
- Backend server running on Port 8000
- Supabase project configured

### Steps

1. **Navigate to folder**:
   ```bash
   cd mobile
   ```

2. **Install Dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run App**:
   ```bash
   flutter run
   ```

### ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection Refused | Check `lib/config.dart` - use correct IP |
| Permission Denied (Mic) | Grant microphone permission in device settings |
| Camera Black Screen | Grant camera permission in device settings |
| Auth Failed | Verify Supabase credentials in `core/supabase_config.dart` |

---

## 📖 Code Documentation

All Dart files include module-level documentation headers following this format:

```dart
/// ==============================================================================
/// MODULE: [File Name]
/// ==============================================================================
///
/// [Description of the module's purpose and features]
/// ==============================================================================
library;
```

---
*Documentation updated 02 Feb 2026*
