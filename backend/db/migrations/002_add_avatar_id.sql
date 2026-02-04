-- Add avatar_id to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_id VARCHAR(50);
