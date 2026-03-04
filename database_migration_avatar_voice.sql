-- Migration: Move voice configuration from Tenant to Avatar
-- Date: 2026-03-04

-- Step 1: Add new columns to avatars table
ALTER TABLE avatars 
ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT 'female',
ADD COLUMN IF NOT EXISTS voice_provider VARCHAR(50) DEFAULT 'google',
ADD COLUMN IF NOT EXISTS voice_name VARCHAR(100) DEFAULT 'en-US-Neural2-F';

-- Step 2: Remove old voice column from avatars
ALTER TABLE avatars DROP COLUMN IF EXISTS default_voice;

-- Step 3: Add new columns to tenants table
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS pitch FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS volume FLOAT DEFAULT 1.0;

-- Step 4: Remove old voice columns from tenants
ALTER TABLE tenants 
DROP COLUMN IF EXISTS voice_model,
DROP COLUMN IF EXISTS voice_gender;

-- Step 5: Update existing avatars with default voice configuration
UPDATE avatars 
SET gender = 'female', 
    voice_provider = 'google', 
    voice_name = 'en-US-Neural2-F'
WHERE gender IS NULL;

-- Step 6: Create index for faster avatar lookups
CREATE INDEX IF NOT EXISTS idx_avatars_gender ON avatars(gender);
CREATE INDEX IF NOT EXISTS idx_tenants_avatar_id ON tenants(avatar_id);

-- Verification queries
-- SELECT id, name, gender, voice_name FROM avatars;
-- SELECT id, company_name, avatar_id, speaking_rate, pitch FROM tenants;
