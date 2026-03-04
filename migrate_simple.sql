-- Add Gemini columns to existing database (without pgvector for now)
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS gemini_api_key_encrypted TEXT;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS voice_gender VARCHAR(20) DEFAULT 'female';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS speaking_rate FLOAT DEFAULT 1.0;
