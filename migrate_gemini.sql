-- Add Gemini columns to existing database
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS gemini_api_key_encrypted TEXT;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS voice_gender VARCHAR(20) DEFAULT 'female';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS speaking_rate FLOAT DEFAULT 1.0;

-- Add embedding column to knowledge_base
ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS embedding vector(768);

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
