-- Migration: Change Avatar storage from URL to Base64
-- Run this after updating code

-- Add new column
ALTER TABLE avatars ADD COLUMN IF NOT EXISTS image_data TEXT;

-- For existing avatars, you'll need to manually re-upload them
-- Or keep both columns temporarily during migration

-- After all avatars are migrated, drop old column:
-- ALTER TABLE avatars DROP COLUMN IF EXISTS image_url;

-- Verify migration
SELECT id, name, 
       CASE 
           WHEN image_data IS NOT NULL THEN 'Migrated'
           ELSE 'Needs Migration'
       END as status
FROM avatars;
