# Database Migration Guide

## Single Unified Migration File

**File:** `database_migration.sql`

This file contains ALL database setup and fixes in one place:
- Table creation
- Column additions
- Index creation
- Domain fixes
- Data validation
- Cleanup
- Summary report

---

## How to Run

### Option 1: Docker (Recommended)

```bash
# Copy SQL file into container and run
docker cp database_migration.sql voice-agent-per_db-gpt-auido-mini-db-1:/tmp/
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant -f /tmp/database_migration.sql
```

### Option 2: Docker Exec (One Command)

```bash
cat database_migration.sql | docker exec -i voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant
```

### Option 3: Local PostgreSQL

```bash
psql -U postgres -d voice_agent_multi_tenant -f database_migration.sql
```

---

## What It Does

### 1. Creates Tables
- `tenants` - Multi-tenant configuration
- `avatars` - Avatar images (base64)
- `knowledge_base` - Company knowledge
- `conversations` - Chat history

### 2. Adds Missing Columns
- `avatars.image_data` - Base64 image storage

### 3. Creates Indexes
- Performance optimization for queries
- Tenant isolation
- Fast lookups

### 4. Fixes Domains
- Updates all domains to `localhost` for development
- Enables local testing

### 5. Validates Data
- Checks for missing widget signatures
- Checks for missing avatar images
- Reports issues

### 6. Cleanup
- Removes old `image_url` column
- Keeps database clean

### 7. Summary Report
- Shows record counts
- Lists all tenants
- Lists all avatars
- Confirms success

---

## After Running Migration

### 1. Restart Backend

```bash
docker-compose restart backend
```

### 2. Verify

```bash
# Check health
curl http://localhost:8000/health

# Check avatars endpoint
curl http://localhost:8000/admin/avatars

# Should return: []
```

### 3. Open Admin Dashboard

```
http://localhost:3000
```

### 4. Create Test Data

1. Go to "Avatar Gallery"
2. Create an avatar
3. Go to "Tenants"
4. Create a tenant with domain = `localhost`

---

## Troubleshooting

### Error: "database does not exist"

```bash
# Create database first
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -c "CREATE DATABASE voice_agent_multi_tenant;"
```

### Error: "permission denied"

```bash
# Use postgres user
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant -f /tmp/database_migration.sql
```

### Want to Start Fresh?

```bash
# Drop and recreate database
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -c "DROP DATABASE IF EXISTS voice_agent_multi_tenant;"
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -c "CREATE DATABASE voice_agent_multi_tenant;"

# Run migration
cat database_migration.sql | docker exec -i voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant
```

---

## Migration is Idempotent

You can run this file multiple times safely:
- Uses `IF NOT EXISTS` for tables
- Uses `IF NOT EXISTS` for indexes
- Checks before adding columns
- Won't duplicate data

---

## Quick Command Reference

```bash
# Run migration
cat database_migration.sql | docker exec -i voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant

# Check tables
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant -c "\dt"

# Check avatars table schema
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant -c "\d avatars"

# Count records
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant -c "SELECT 'tenants' as table, COUNT(*) FROM tenants UNION ALL SELECT 'avatars', COUNT(*) FROM avatars;"

# Restart backend
docker-compose restart backend
```

---

**Run the migration and you're ready to go!** 🚀
