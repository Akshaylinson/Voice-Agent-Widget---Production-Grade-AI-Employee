-- Migration: OpenRouter to Gemini with pgvector RAG
-- Run this on existing database to upgrade

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add new columns to tenants table
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS gemini_api_key_encrypted TEXT,
ADD COLUMN IF NOT EXISTS voice_gender VARCHAR(20) DEFAULT 'female',
ADD COLUMN IF NOT EXISTS speaking_rate FLOAT DEFAULT 1.0;

-- Rename old column (optional - keep both for backward compatibility)
-- ALTER TABLE tenants RENAME COLUMN openai_api_key_encrypted TO gemini_api_key_encrypted;

-- Add embedding column to knowledge_base
ALTER TABLE knowledge_base 
ADD COLUMN IF NOT EXISTS embedding vector(768);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Update default voice models
UPDATE tenants SET voice_model = 'Puck' WHERE voice_model = 'nova';
UPDATE tenants SET voice_model = 'Charon' WHERE voice_model = 'onyx';
UPDATE avatars SET default_voice = 'Puck' WHERE default_voice = 'nova';

-- Add comment
COMMENT ON COLUMN knowledge_base.embedding IS 'Gemini text-embedding-004 vector (768 dimensions)';
