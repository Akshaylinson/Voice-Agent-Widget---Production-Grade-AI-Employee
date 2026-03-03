-- ============================================
-- Voice Agent Platform - Database Migration
-- Complete Schema Setup and Fixes
-- ============================================

-- Run this file once to set up or fix your database
-- Usage: psql -U postgres -d voice_agent_multi_tenant -f database_migration.sql

\echo '=========================================='
\echo 'Starting Voice Agent Database Migration'
\echo '=========================================='

-- ============================================
-- 1. CREATE TABLES (if not exist)
-- ============================================

\echo 'Creating tables...'

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    avatar_id UUID,
    introduction_script TEXT,
    voice_model VARCHAR(50) DEFAULT 'nova',
    voice_tone VARCHAR(50) DEFAULT 'friendly',
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 500,
    openai_api_key_encrypted TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    brand_colors JSON,
    widget_signature VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    image_data TEXT,
    default_voice VARCHAR(50) DEFAULT 'nova',
    personality_prompt TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    transcript TEXT,
    response TEXT,
    token_usage INTEGER,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

\echo 'Tables created successfully'

-- ============================================
-- 2. ADD MISSING COLUMNS (if not exist)
-- ============================================

\echo 'Adding missing columns...'

-- Add image_data to avatars if missing
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'avatars' AND column_name = 'image_data'
    ) THEN
        ALTER TABLE avatars ADD COLUMN image_data TEXT;
        RAISE NOTICE 'Added image_data column to avatars table';
    ELSE
        RAISE NOTICE 'image_data column already exists';
    END IF;
END $$;

-- Make image_data nullable (for migration)
ALTER TABLE avatars ALTER COLUMN image_data DROP NOT NULL;

\echo 'Columns updated successfully'

-- ============================================
-- 3. CREATE INDEXES
-- ============================================

\echo 'Creating indexes...'

CREATE INDEX IF NOT EXISTS idx_tenant_domain ON tenants(domain);
CREATE INDEX IF NOT EXISTS idx_tenant_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_tenant ON knowledge_base(tenant_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_active ON knowledge_base(is_active);
CREATE INDEX IF NOT EXISTS idx_conversation_tenant ON conversations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversations(created_at);

\echo 'Indexes created successfully'

-- ============================================
-- 4. FIX DOMAIN VALIDATION
-- ============================================

\echo 'Fixing tenant domains for localhost testing...'

-- Update any non-localhost domains to localhost for development
UPDATE tenants 
SET domain = 'localhost' 
WHERE domain NOT LIKE '%localhost%' 
  AND domain NOT LIKE '%127.0.0.1%';

\echo 'Domains updated for localhost testing'

-- ============================================
-- 5. DATA VALIDATION
-- ============================================

\echo 'Validating data...'

-- Check for tenants without widget signatures
DO $$
DECLARE
    missing_sig_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing_sig_count
    FROM tenants
    WHERE widget_signature IS NULL OR widget_signature = '';
    
    IF missing_sig_count > 0 THEN
        RAISE NOTICE 'Warning: % tenants missing widget signatures', missing_sig_count;
    ELSE
        RAISE NOTICE 'All tenants have widget signatures';
    END IF;
END $$;

-- Check for avatars without image data
DO $$
DECLARE
    missing_img_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing_img_count
    FROM avatars
    WHERE image_data IS NULL OR image_data = '';
    
    IF missing_img_count > 0 THEN
        RAISE NOTICE 'Warning: % avatars missing image data', missing_img_count;
    ELSE
        RAISE NOTICE 'All avatars have image data';
    END IF;
END $$;

\echo 'Data validation complete'

-- ============================================
-- 6. CLEANUP OLD COLUMNS (optional)
-- ============================================

\echo 'Cleaning up old columns...'

-- Drop image_url column if it exists (we now use image_data)
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'avatars' AND column_name = 'image_url'
    ) THEN
        ALTER TABLE avatars DROP COLUMN image_url;
        RAISE NOTICE 'Dropped old image_url column';
    ELSE
        RAISE NOTICE 'No old columns to clean up';
    END IF;
END $$;

\echo 'Cleanup complete'

-- ============================================
-- 7. SUMMARY REPORT
-- ============================================

\echo '=========================================='
\echo 'Migration Summary'
\echo '=========================================='

SELECT 
    'Tenants' as table_name,
    COUNT(*) as record_count
FROM tenants
UNION ALL
SELECT 
    'Avatars' as table_name,
    COUNT(*) as record_count
FROM avatars
UNION ALL
SELECT 
    'Knowledge Base' as table_name,
    COUNT(*) as record_count
FROM knowledge_base
UNION ALL
SELECT 
    'Conversations' as table_name,
    COUNT(*) as record_count
FROM conversations;

\echo ''
\echo 'Tenant Details:'
SELECT 
    id,
    company_name,
    domain,
    status,
    CASE WHEN avatar_id IS NOT NULL THEN 'Yes' ELSE 'No' END as has_avatar,
    created_at
FROM tenants
ORDER BY created_at DESC;

\echo ''
\echo 'Avatar Details:'
SELECT 
    id,
    name,
    CASE 
        WHEN image_data IS NOT NULL AND LENGTH(image_data) > 0 THEN 'Yes'
        ELSE 'No'
    END as has_image,
    created_at
FROM avatars
ORDER BY created_at DESC;

\echo ''
\echo '=========================================='
\echo 'Migration Complete!'
\echo '=========================================='
\echo 'Next steps:'
\echo '1. Restart backend: docker-compose restart backend'
\echo '2. Open admin dashboard: http://localhost:3000'
\echo '3. Create avatars and tenants'
\echo '=========================================='
