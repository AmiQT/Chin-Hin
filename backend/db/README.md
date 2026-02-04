# Database Setup Guide

## 🚀 Quick Setup (Supabase)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy your:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Key**: `eyJhbGciOiJ...`

### Step 2: Update Environment

```bash
# Copy .env.example to .env
cp ../.env.example ../.env

# Edit .env with your Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Step 3: Run Migrations

1. Open Supabase Dashboard → **SQL Editor**
2. Run these files in order:
   - `migrations/001_initial_schema.sql` - Creates tables
   - `migrations/002_dummy_data.sql` - Adds test data

### Step 4: Verify

Check **Table Editor** in Supabase Dashboard:
- ✅ users (10 rows)
- ✅ leave_types (6 rows)
- ✅ leave_balances
- ✅ rooms (5 rows)
- ✅ claim_categories (5 rows)

---

## 📊 Schema Overview

```
users ──────────┬──→ leave_balances ──→ leave_types
                ├──→ leave_requests ──→ leave_types
                ├──→ room_bookings ──→ rooms
                ├──→ claims ──→ claim_categories
                └──→ conversations ──→ messages
```

---

## 🧪 Test Queries

```sql
-- Check all users
SELECT * FROM users;

-- Check Ahmad's leave balance
SELECT u.full_name, lt.name, lb.total_days, lb.used_days
FROM leave_balances lb
JOIN users u ON lb.user_id = u.id
JOIN leave_types lt ON lb.leave_type_id = lt.id
WHERE u.email = 'ahmad@chinhin.com';

-- Check pending claims
SELECT u.full_name, c.amount, cc.name as category, c.status
FROM claims c
JOIN users u ON c.user_id = u.id
JOIN claim_categories cc ON c.category_id = cc.id
WHERE c.status = 'pending';
```

---

*Ready for Phase 3: API Endpoints! 🔥*
