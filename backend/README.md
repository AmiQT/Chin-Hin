# Chin Hin Employee AI Assistant - Backend

> FastAPI backend untuk AI-powered employee assistant 🚀

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI Engine**: Gemini 2.5 Flash + LangGraph
- **Embeddings**: Gemini text-embedding-004
- **Nudge Engine**: Background Asyncio Tasks

## Quick Start

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup Database
# 1. Run migrations in db/migrations/*.sql on Supabase
# 2. Seed Knowledge Base for RAG:
python seed_rag.py

# Run development server
uvicorn app.main:app --reload
```

## Testing God Mode 🤖

```bash
# Test RAG (HR Policies)
python test_rag_chat.py

# Test Proactive Nudges
python test_nudges.py
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/         # Endpoints (Chat, Claims, Nudges, etc)
│   ├── agents/         # AI Logic (function_agent.py, gemini_client.py)
│   ├── services/       # NudgeService, EmbeddingService
│   └── main.py         # App Entry + Background Scheduler
├── db/
│   └── migrations/     # SQL Schema (001 to 004)
├── seed_rag.py         # Seed HR Policies
├── test_nudges.py      # Verification Script
└── requirements.txt
```

---

*Phase 4 & 5 Complete! ✅ Advanced AI & Proactive Engine delivered.*
