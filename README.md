<p align="center">
  <img src="https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white" alt="Flutter"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</p>

<h1 align="center">🚀 Chin Hin Employee AI Assistant</h1>

<p align="center">
  <strong>AI-powered employee assistant dengan natural language interface</strong>
  <br/>
  <em>Business Challenge 5: Enable Seamless User Journey for Employee App</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-documentation">Docs</a>
</p>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🧠 AI-Powered Chat
- Natural language understanding
- Context-aware conversations  
- Multimodal input (text, voice, images)
- RAG-enhanced HR policy answers

</td>
<td width="50%">

### 👁️ Live Vision (Gemini 2.0)
- Real-time camera streaming
- Audio capture & processing
- WebSocket-based communication
- Ephemeral token security

</td>
</tr>
<tr>
<td width="50%">

### 📋 Employee Services
- Leave management & tracking
- Expense claims with OCR
- Meeting room booking
- Profile & stats dashboard

</td>
<td width="50%">

### 🔔 Proactive Nudges
- AI-generated reminders
- Smart notifications
- Context-aware suggestions
- Background processing

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

<table>
<tr><th>Layer</th><th>Technology</th><th>Purpose</th></tr>
<tr><td>🖥️ Backend</td><td>FastAPI + Python 3.11</td><td>REST API & WebSocket</td></tr>
<tr><td>🤖 AI Engine</td><td>Gemini 2.5 Flash + LangGraph</td><td>Conversational AI</td></tr>
<tr><td>👁️ Live Vision</td><td>Gemini 2.0 Flash</td><td>Real-time multimodal</td></tr>
<tr><td>📚 RAG</td><td>Gemini Embeddings + pgvector</td><td>HR policy retrieval</td></tr>
<tr><td>🗄️ Database</td><td>In-Memory / Local Mock</td><td>Data persistence (dev mode)</td></tr>
<tr><td>🔐 Auth</td><td>Simple Token Auth</td><td>JWT-style authentication</td></tr>
<tr><td>📱 Mobile</td><td>Flutter + Riverpod + ShadCN UI</td><td>Cross-platform app</td></tr>
<tr><td>☁️ Deploy</td><td>AWS EC2 / Azure Container Apps</td><td>Cloud hosting</td></tr>
</table>

---

## 📁 Project Structure

```
Chin Hin/
├── 📂 backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # REST endpoints
│   │   ├── agents/         # Gemini AI integration
│   │   └── services/       # Business logic
│   └── db/migrations/      # SQL schemas
│
├── 📱 mobile/               # Flutter Mobile App
│   └── lib/
│       ├── screens/        # UI screens (8 screens)
│       ├── providers/      # Riverpod state (3 providers)
│       ├── services/       # API & WebSocket
│       └── widgets/        # Generative UI components
│
└── 📚 docs/                 # Documentation
    ├── API.md              # API reference
    └── frontend_documentation.md
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
✅ Python 3.11+
✅ Flutter SDK 3.x
✅ Azure OpenAI API Key
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env       # Add your API keys

# Run server
uvicorn app.main:app --reload
```

### Mobile Setup

```bash
cd mobile

# Install dependencies
flutter pub get

# Run app
flutter run
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | AI chat (multimodal) |
| `/api/v1/nudges` | GET | Proactive notifications |
| `/api/v1/leaves/balance` | GET | Leave balance |
| `/api/v1/leaves` | POST | Apply leave |
| `/api/v1/claims` | POST | Submit expense |
| `/api/v1/rooms` | GET | Available rooms |
| `/api/v1/rooms/book` | POST | Book room |
| `/api/v1/live-vision/token` | GET | Ephemeral token |

> 📖 Full documentation: [docs/API.md](docs/API.md)

---

## ⚙️ Environment Variables

Create `backend/.env`:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

---

## 📊 Project Status

| Phase | Description | Status |
|:-----:|-------------|:------:|
| 1 | Project Setup | ✅ |
| 2 | Auth & Mock Data | ✅ |
| 3 | Basic REST API | ✅ |
| 4 | AI Engine (RAG + Multimodal) | ✅ |
| 5 | Proactive Nudges | ✅ |
| 6 | Mobile Integration | ✅ |
| 7 | Persona & Polish | ✅ |
| 8 | Live Vision (Gemini 2.0) | ✅ |
| 9 | Code Documentation | ✅ |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete API documentation |
| [Frontend Docs](docs/frontend_documentation.md) | Mobile app architecture |
| [AWS Deployment](docs/AWS_DEPLOYMENT.md) | EC2 deployment dengan Cloudflare Tunnel |
| [Quick Start EC2](docs/QUICK_START_EC2.md) | Rapid EC2 deployment guide |
| [Azure Deployment](docs/DEPLOYMENT.md) | Azure Container Apps steps |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ for Chin Hin Group</strong>
  <br/>
  <sub>© 2026 Chin Hin Employee AI Assistant</sub>
</p>
