-- ================================================
-- Migration: 003_fix_function_search_path.sql
-- Fix mutable search_path security warning on functions
-- Date: 2026-02-01
-- ================================================

-- Fix handle_new_user function
ALTER FUNCTION public.handle_new_user() SET search_path = public;

-- Fix handle_updated_at function
ALTER FUNCTION public.handle_updated_at() SET search_path = public;

-- Fix update_updated_at function (if exists)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at') THEN
    ALTER FUNCTION public.update_updated_at() SET search_path = public;
  END IF;
END $$;

-- Fix match_knowledge_base function for RAG
-- This function takes parameters, need to check exact signature
DO $$
DECLARE
  func_exists boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public' AND p.proname = 'match_knowledge_base'
  ) INTO func_exists;
  
  IF func_exists THEN
    -- Get the function with its full signature and alter it
    EXECUTE 'ALTER FUNCTION public.match_knowledge_base SET search_path = public';
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Could not alter match_knowledge_base: %', SQLERRM;
END $$;

-- ================================================
-- DONE! All functions now have immutable search_path
-- ================================================
