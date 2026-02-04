# 🔧 Backend Developer Rules

> **Role**: Backend Developer untuk Chin Hin Employee AI Assistant
> **Fokus**: API development, AI agent logic, database, authentication
> **Boundary**: JANGAN sentuh frontend/mobile code

---

## 📋 Responsibilities

### ✅ DALAM SCOPE (Tugas Kita)

| Area | Tasks |
|------|-------|
| **FastAPI** | REST/WebSocket endpoints, request handling, middleware |
| **LangGraph** | AI agent orchestration, tool definitions, memory management |
| **Database** | PostgreSQL schema, migrations, queries, pgvector setup |
| **Authentication** | Azure AD B2C integration, JWT handling, RLS |
| **Gemini API** | LLM integration, prompt engineering, smart routing |
| **OCR** | Receipt processing, document parsing |
| **Redis** | Caching, session management |
| **DevOps** | Dockerfile, CI/CD pipelines, Azure Container Apps |

### ❌ LUAR SCOPE (Jangan Sentuh)

| Area | Reason |
|------|--------|
| **Flutter/Mobile** | Frontend agent handle |
| **UI/UX Design** | Bukan tugas kita |
| **Mobile State Management** | Riverpod/BLoC = frontend |
| **Push Notification Client** | Mobile side |

---

## 🏗️ Tech Stack

```
Backend Framework:  FastAPI
AI Orchestration:   LangGraph
LLM:                Gemini API (Flash + Pro)
Database:           Supabase (PostgreSQL + pgvector)
Cache:              Upstash Redis (optional for MVP)
Auth:               Supabase Auth
Container:          Docker → Azure Container Apps
OCR:                Google Vision API
Monitoring:         Langfuse (AI Observability)
```

---

## 📁 Folder Structure (Recommended)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Environment config
│   ├── dependencies.py      # Shared dependencies
│   │
│   ├── api/                 # REST endpoints
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── leaves.py
│   │   │   ├── bookings.py
│   │   │   └── claims.py
│   │   └── websocket.py     # Real-time chat
│   │
│   ├── agents/              # LangGraph AI agents
│   │   ├── main_agent.py    # Primary agent
│   │   ├── tools/           # Agent tools
│   │   │   ├── leave_tool.py
│   │   │   ├── booking_tool.py
│   │   │   ├── claim_tool.py
│   │   │   └── notification_tool.py
│   │   ├── memory/          # Conversation memory
│   │   └── prompts/         # System prompts
│   │
│   ├── services/            # Business logic
│   │   ├── leave_service.py
│   │   ├── booking_service.py
│   │   ├── claim_service.py
│   │   └── ocr_service.py
│   │
│   ├── models/              # Pydantic & SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── db_models.py     # SQLAlchemy models
│   │
│   ├── db/                  # Database layer
│   │   ├── connection.py
│   │   ├── migrations/
│   │   └── repositories/
│   │
│   └── utils/               # Helpers
│       ├── security.py
│       ├── validators.py
│       └── logging.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── alembic.ini
```

---

## 🛡️ Security Guidelines

### 1. Authentication
- Use Azure AD B2C for all auth
- Validate JWT tokens on every request
- Implement refresh token rotation

### 2. Data Protection
- Apply Row Level Security (RLS) di database
- Mask sensitive data dalam logs (IC, phone, salary)
- Encrypt data at rest dan in transit

### 3. AI Safety
- Confirmation step untuk critical actions
- Structured output (Pydantic) untuk prevent hallucination
- Validate semua AI output sebelum execute
- Rate limiting untuk prevent abuse

---

## 📝 Coding Standards

### Python Style
- Follow PEP 8
- Use type hints everywhere
- Docstrings untuk semua functions
- Black formatter, isort, ruff

### API Design
- RESTful conventions
- Versioned endpoints (/api/v1/)
- Standardized response format
- Proper HTTP status codes

### Error Handling
```python
# Standard error response
{
    "success": false,
    "error": {
        "code": "LEAVE_INSUFFICIENT_BALANCE",
        "message": "Baki cuti tidak mencukupi",
        "details": {...}
    }
}
```

---

## 🔄 Workflow Rules

1. **Always** check existing code sebelum implement
2. **Always** write tests untuk features baru
3. **Never** hardcode credentials - guna environment variables
4. **Never** log sensitive user data
5. **Always** handle errors gracefully
6. **Document** API endpoints dengan OpenAPI/Swagger

---

## 📊 Communication with Frontend Agent

### API Contract
- Maintain OpenAPI spec (`openapi.yaml`)
- Update bila ada endpoint changes
- Include request/response examples

### Handoff Points
- `/api/v1/*` - REST endpoints
- `/ws/chat` - WebSocket untuk real-time
- Response format: JSON dengan standard structure

---

*Last Updated: 25 Jan 2026*
