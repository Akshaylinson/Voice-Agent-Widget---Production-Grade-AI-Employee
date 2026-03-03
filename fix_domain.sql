-- Check current tenant domain
SELECT id, company_name, domain, status FROM tenants WHERE id = 'e78f6bbe-4cf0-471c-82cc-20f29a08506f';

-- Update domain to localhost
UPDATE tenants SET domain = 'localhost' WHERE id = 'e78f6bbe-4cf0-471c-82cc-20f29a08506f';

-- Verify update
SELECT id, company_name, domain, status FROM tenants WHERE id = 'e78f6bbe-4cf0-471c-82cc-20f29a08506f';
