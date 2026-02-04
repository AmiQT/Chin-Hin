# Chin Hin Employee AI Assistant - Panduan AI Agent 🚀

> Yo AI agents! Ni panduan untuk kau code dalam repo ni. Baca dulu sebelum start! 💪

## Big Picture Architecture

**Monorepo vibes**: Backend (FastAPI) + Mobile (Flutter) untuk employee self-service app dengan AI chat yang boleh cakap BM/EN! 🇲🇾

```
backend/        → FastAPI + Gemini AI + Supabase PostgreSQL
mobile/         → Flutter + Riverpod + Dio  
docs/           → API.md (semua endpoint ada sini)
```

**Flow dia macam ni**: Mobile panggil REST API → API route ke Gemini → Gemini tolong user dengan cuti/claims/bilik meeting

## Backend (Python/FastAPI)

### Structure Dia Macam Mana
- **Routers**: `app/api/v1/{domain}.py` - Setiap feature ada router sendiri (e.g., `/chat`, `/leaves`)
- **Entry point**: [app/main.py](../backend/app/main.py) register semua router dengan prefix `/api/v1`
- **Schemas**: [app/models/schemas.py](../backend/app/models/schemas.py) - Semua Pydantic models (User, Leave, Claim, dll)
- **AI Agent**: [app/agents/gemini_client.py](../backend/app/agents/gemini_client.py) - Integration Gemini dengan bilingual prompt

### Config & Setup
- **Settings**: [app/config.py](../backend/app/config.py) pakai `pydantic_settings` baca dari `.env`
- **Env vars wajib**: `SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`
- **Import**: `from app.config import get_settings` → `settings = get_settings()`

### Nak Run Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate     # Windows je
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- API docs: `http://localhost:8000/docs` (Swagger UI - best gila!)
- Docker: `docker-compose up` (tengok [docker-compose.yml](../backend/docker-compose.yml))

### Testing Pattern
```bash
cd backend
pytest tests/ -v
```
- Fixtures kat [tests/conftest.py](../backend/tests/conftest.py) ada `client` (TestClient)
- Pattern: `def test_{feature}_endpoint(client)` → `response = client.get(...)`

### AI Chat Flow
- **Bilingual prompt**: Check `SYSTEM_PROMPT` dalam [gemini_client.py](../backend/app/agents/gemini_client.py) - campur BM + EN
- **Model routing**: `get_model(task_type)` pilih `gemini-1.5-flash` (senang) atau `gemini-1.5-pro` (complex)
- **API flow**: POST `/api/v1/chat` → `chat_completion()` → dapat response dari Gemini

## Mobile (Flutter/Dart)

### State Management
- **Riverpod 3.x**: Semua state guna providers dalam `lib/providers/`
  - [user_provider.dart](../mobile/lib/providers/user_provider.dart) - Auth state (userId, login)
  - [chat_provider.dart](../mobile/lib/providers/chat_provider.dart) - Chat messages & API calls

### API Setup
- **Service**: [api_service.dart](../mobile/lib/services/api_service.dart) pakai Dio
- **Base URL**: [config.dart](../mobile/lib/config.dart) - Android emulator guna `10.0.2.2:8000`, iOS guna `localhost:8000`
- **Test user**: Default userId `11111111-1111-1111-1111-111111111111` dalam Config

### Run Mobile App
```bash
cd mobile
flutter pub get
flutter run
```
- Pastikan backend dah run kat `localhost:8000`
- Kalau guna physical device: Tukar `Config.baseUrl` ke LAN IP PC kau

## Conventions Yang Penting

### Response Format (Backend)
Semua API endpoint return format standard ni:
```python
{"success": bool, "message": str, "data": {...}}
```
Full reference tengok [API.md](../docs/API.md)

### Database Access
- **Takde ORM**: Terus call Supabase client je
- **Migrations**: SQL files dalam `backend/db/migrations/` (run manual kat Supabase SQL Editor)
- **Dummy data**: `002_dummy_data.sql` untuk dev

### Core Module
- **Validators**: `from app.core import validate_uuid, validate_date, sanitize_string`
- **Exceptions**: `from app.core import NotFoundError, ForbiddenError`
- **Logging**: Auto-configured, just use `logging.getLogger(__name__)`

### Bilingual Support
- **Backend**: AI response support BM/EN mix ("Nak apply cuti" → "Leave request created! 🎉")
- **Mobile**: UI English, tapi chat boleh terima input BM

## Common Tasks

**Nak tambah API endpoint baru**:
1. Create router dalam `backend/app/api/v1/{feature}.py` dengan `APIRouter(prefix="/feature", tags=[...])`
2. Register kat [main.py](../backend/app/main.py): `app.include_router(router, prefix="/api/v1")`
3. Tambah schemas dalam [schemas.py](../backend/app/models/schemas.py)

**Nak buat Flutter screen baru**:
1. Create kat `mobile/lib/screens/{screen}_screen.dart`
2. Add route dalam [main.dart](../mobile/lib/main.dart) MaterialApp
3. Kalau perlu, buat provider dalam `lib/providers/`

**Nak update AI behavior**: Edit `SYSTEM_PROMPT` dalam [gemini_client.py](../backend/app/agents/gemini_client.py)

## Dev Notes (Penting!)
- **CORS**: Backend allow semua origins (`allow_origins=["*"]`) - kena update untuk production nanti
- **Auth**: Sekarang dummy je (guna test userId) - real auth still pending
- **Deployment**: Target Azure Container Apps (backend), mobile belum deploy lagi
