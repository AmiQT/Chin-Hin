# 📡 Chin Hin Backend API Documentation

> **Base URL**: `http://localhost:8000`
> **Swagger UI**: `http://localhost:8000/docs`

---

## 🔐 Authentication

Currently using dummy auth. User ID required in requests.

**Default Test User**:
```
user_id: 11111111-1111-1111-1111-111111111111
name: Ahmad bin Hassan
```

---

## 📋 API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API status |
| GET | `/` | App info |

---

### 👤 Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List all users |
| GET | `/api/v1/users/{user_id}` | Get single user |
| GET | `/api/v1/users/{user_id}/leaves` | User's leave requests |
| GET | `/api/v1/users/{user_id}/claims` | User's expense claims |

**Query Params** (GET `/users`):
- `department` - Filter by department
- `role` - Filter by role (employee, manager, hr, admin)

---

### 🏖️ Leave Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/leaves/types` | Get leave types |
| GET | `/api/v1/leaves` | List leave requests |
| GET | `/api/v1/leaves/{leave_id}` | Get single request |
| POST | `/api/v1/leaves` | Create leave request |
| PATCH | `/api/v1/leaves/{leave_id}/approve` | Approve leave |
| PATCH | `/api/v1/leaves/{leave_id}/reject` | Reject leave |

**POST `/api/v1/leaves` Params**:
```
user_id: string (required)
leave_type_id: string (required) - "lt-annual", "lt-mc", "lt-emergency"
start_date: date (required) - "2026-02-01"
end_date: date (required) - "2026-02-03"
reason: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Leave request created! 🎉",
  "data": {
    "id": "lr-abc123",
    "user_id": "...",
    "status": "pending",
    "total_days": 3
  }
}
```

---

### 🏢 Room Booking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rooms` | List rooms |
| GET | `/api/v1/rooms/{room_id}` | Get room details |
| GET | `/api/v1/rooms/{room_id}/bookings` | Room's bookings |
| GET | `/api/v1/rooms/bookings/all` | All bookings |
| POST | `/api/v1/rooms/bookings` | Create booking |
| DELETE | `/api/v1/rooms/bookings/{booking_id}` | Cancel booking |

**POST `/api/v1/rooms/bookings` Params**:
```
room_id: string (required) - "room-001", "room-002", "room-003"
user_id: string (required)
title: string (required)
start_time: datetime (required) - "2026-01-27T09:00:00"
end_time: datetime (required) - "2026-01-27T11:00:00"
description: string (optional)
```

---

### 💰 Expense Claims

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/claims/categories` | Get categories |
| GET | `/api/v1/claims` | List claims |
| GET | `/api/v1/claims/{claim_id}` | Get single claim |
| POST | `/api/v1/claims` | Submit claim |
| PATCH | `/api/v1/claims/{claim_id}/approve` | Approve claim |
| PATCH | `/api/v1/claims/{claim_id}/reject` | Reject claim |
| POST | `/api/v1/claims/{claim_id}/receipt` | Upload receipt |

**POST `/api/v1/claims` Params**:
```
user_id: string (required)
category_id: string (required) - "cat-transport", "cat-meals", "cat-parking"
amount: float (required)
description: string (optional)
claim_date: date (optional)
```

**Categories**:
| ID | Name | Max Amount |
|----|------|------------|
| cat-transport | Transport | RM500 |
| cat-meals | Meals | RM200 |
| cat-parking | Parking | RM100 |

---

### 🤖 AI Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message |
| GET | `/api/v1/chat/conversations` | List conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation |
| DELETE | `/api/v1/chat/conversations/{id}` | Delete conversation |
| GET | `/api/v1/chat/test` | Quick AI test |

**POST `/api/v1/chat` Body**:
```json
{
  "message": "Nak apply cuti esok",
  "conversation_id": "conv-abc123",
  "user_id": "11111111-1111-1111-1111-111111111111"
}
```

**Response**:
```json
{
  "success": true,
  "conversation_id": "conv-abc123",
  "message": "Nak apply cuti esok",
  "response": "OK! Nak apply cuti untuk bila? 📅"
}
```

> ⚠️ **Note**: AI requires GEMINI_API_KEY in `.env` to function.

---

## 📦 Response Format

All endpoints return:
```json
{
  "success": true,
  "data": [...],
  "total": 5,
  "message": "Optional message"
}
```

**Error Response**:
```json
{
  "detail": "Error message here"
}
```

---

## 🧪 Test Users

| ID | Name | Department | Role |
|----|------|------------|------|
| 11111111-... | Ahmad bin Hassan | Engineering | employee |
| 22222222-... | Siti Nurhaliza | HR | hr |
| 33333333-... | Raj Kumar | Finance | employee |
| 44444444-... | Tan Mei Ling | Marketing | manager |
| 55555555-... | Farid Abdullah | Engineering | manager |

---

## 🚀 Quick Start

```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs

---

*Last Updated: 25 Jan 2026*
