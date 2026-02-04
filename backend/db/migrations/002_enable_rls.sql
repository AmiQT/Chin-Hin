-- ================================================
-- Migration: 002_enable_rls.sql
-- Enable Row Level Security on all public tables
-- Date: 2026-02-01
-- ================================================

-- ================================================
-- STEP 1: Enable RLS on all tables
-- ================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claim_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nudges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;

-- ================================================
-- STEP 2: Create RLS Policies
-- ================================================

-- ==== USERS TABLE ====
-- Users can read their own profile
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Service role can do everything (for backend)
CREATE POLICY "users_service_all" ON public.users
  FOR ALL USING (auth.role() = 'service_role');

-- ==== LEAVE TYPES (Public Read) ====
CREATE POLICY "leave_types_select_all" ON public.leave_types
  FOR SELECT USING (true);

CREATE POLICY "leave_types_service_all" ON public.leave_types
  FOR ALL USING (auth.role() = 'service_role');

-- ==== LEAVE REQUESTS ====
-- Users can view their own leave requests
CREATE POLICY "leave_requests_select_own" ON public.leave_requests
  FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own leave requests
CREATE POLICY "leave_requests_insert_own" ON public.leave_requests
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own pending requests
CREATE POLICY "leave_requests_update_own" ON public.leave_requests
  FOR UPDATE USING (auth.uid() = user_id AND status = 'pending');

-- Service role can do everything
CREATE POLICY "leave_requests_service_all" ON public.leave_requests
  FOR ALL USING (auth.role() = 'service_role');

-- ==== LEAVE BALANCES ====
CREATE POLICY "leave_balances_select_own" ON public.leave_balances
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "leave_balances_service_all" ON public.leave_balances
  FOR ALL USING (auth.role() = 'service_role');

-- ==== ROOMS (Public Read) ====
CREATE POLICY "rooms_select_all" ON public.rooms
  FOR SELECT USING (true);

CREATE POLICY "rooms_service_all" ON public.rooms
  FOR ALL USING (auth.role() = 'service_role');

-- ==== ROOM BOOKINGS ====
CREATE POLICY "room_bookings_select_own" ON public.room_bookings
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "room_bookings_insert_own" ON public.room_bookings
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "room_bookings_update_own" ON public.room_bookings
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "room_bookings_delete_own" ON public.room_bookings
  FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "room_bookings_service_all" ON public.room_bookings
  FOR ALL USING (auth.role() = 'service_role');

-- ==== CLAIM CATEGORIES (Public Read) ====
CREATE POLICY "claim_categories_select_all" ON public.claim_categories
  FOR SELECT USING (true);

CREATE POLICY "claim_categories_service_all" ON public.claim_categories
  FOR ALL USING (auth.role() = 'service_role');

-- ==== CLAIMS ====
CREATE POLICY "claims_select_own" ON public.claims
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "claims_insert_own" ON public.claims
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "claims_update_own" ON public.claims
  FOR UPDATE USING (auth.uid() = user_id AND status = 'pending');

CREATE POLICY "claims_service_all" ON public.claims
  FOR ALL USING (auth.role() = 'service_role');

-- ==== CONVERSATIONS ====
CREATE POLICY "conversations_select_own" ON public.conversations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "conversations_insert_own" ON public.conversations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "conversations_delete_own" ON public.conversations
  FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "conversations_service_all" ON public.conversations
  FOR ALL USING (auth.role() = 'service_role');

-- ==== MESSAGES ====
-- Users can view messages from their conversations
CREATE POLICY "messages_select_own" ON public.messages
  FOR SELECT USING (
    conversation_id IN (
      SELECT id FROM public.conversations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "messages_insert_own" ON public.messages
  FOR INSERT WITH CHECK (
    conversation_id IN (
      SELECT id FROM public.conversations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "messages_service_all" ON public.messages
  FOR ALL USING (auth.role() = 'service_role');

-- ==== NUDGES ====
CREATE POLICY "nudges_select_own" ON public.nudges
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "nudges_update_own" ON public.nudges
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "nudges_service_all" ON public.nudges
  FOR ALL USING (auth.role() = 'service_role');

-- ==== KNOWLEDGE BASE (Service Role Only) ====
CREATE POLICY "knowledge_base_service_all" ON public.knowledge_base
  FOR ALL USING (auth.role() = 'service_role');

-- ================================================
-- DONE! All tables now have RLS enabled with policies
-- ================================================
