# Docker Deployment Guide

## ✅ Changes Made

### 1. Avatar Storage - No More File Uploads!
- **Before:** Images saved to `/uploads` folder (lost on container restart)
- **After:** Images stored as base64 in PostgreSQL database
- **Benefit:** Persistent storage, no volume management needed

### 2. Live Code Updates
- **Before:** Required rebuild for every code change
- **After:** Source code mounted as volume, changes apply instantly
- **Benefit:** Fast development iteration

### 3. Domain Validation Fixed
- Accepts both `localhost` AND production domain
- Works with Docker networking

---

## 🚀 Quick Start

### Step 1: Start Services

```bash
cd e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### Step 2: Run Database Migration

```bash
# Connect to database
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant

# Run migration
ALTER TABLE avatars ADD COLUMN IF NOT EXISTS image_data TEXT;

# Exit
\q
```

### Step 3: Access Services

- **Backend API:** http://localhost:8000
- **Admin Dashboard:** http://localhost:3000
- **Database:** localhost:5432

---

## 📝 Creating Tenants with Avatars

### 1. Open Admin Dashboard
http://localhost:3000

### 2. Create Avatar First
1. Go to "Avatar Gallery" tab
2. Click "+ Add Avatar"
3. Enter name (e.g., "Sarah AI")
4. Upload image file
5. Click "Create"
6. ✅ Image now stored in database as base64

### 3. Create Tenant
1. Go to "Tenants" tab
2. Fill form:
   - Company Name: Codeless AI
   - Domain: **localhost** ← Important!
   - OpenAI API Key: sk-your-key
   - Avatar: Select "Sarah AI" from dropdown
   - Voice Model: Nova
   - Introduction: "Hello! I'm Sarah from Codeless AI..."
3. Click "Create Tenant"
4. Copy embed code

### 4. Test Widget
1. Update CodelessAi.html with new tenant credentials
2. Open in browser
3. ✅ Avatar appears automatically (from database)
4. ✅ Introduction plays

---

## 🔄 Making Code Changes

### Backend Changes (Python)

```bash
# Edit any file in backend/
# Example: backend/main.py

# Changes apply automatically (--reload flag)
# Check logs:
docker-compose logs -f backend
```

### Admin Dashboard Changes (HTML)

```bash
# Edit admin/index.html

# Rebuild admin container:
docker-compose restart admin

# Or rebuild:
docker-compose build admin
docker-compose up -d admin
```

---

## 🐛 Troubleshooting

### Issue: "Domain not authorized"

**Fix:**
```bash
# Update tenant domain in database
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant

UPDATE tenants SET domain = 'localhost' WHERE company_name = 'Codeless AI';
\q
```

### Issue: Avatar not showing

**Cause:** Old avatars with `image_url` instead of `image_data`

**Fix:** Re-create avatar through admin dashboard (will use base64 storage)

### Issue: Code changes not applying

**Backend:**
```bash
# Check if volume is mounted
docker inspect voice-agent-per_db-gpt-auido-mini-backend-1 | grep Mounts -A 10

# Should show: ./backend:/app

# Restart if needed
docker-compose restart backend
```

**Admin:**
```bash
# Admin needs rebuild
docker-compose build admin
docker-compose up -d admin
```

### Issue: Database connection failed

```bash
# Check database is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart database
docker-compose restart db
```

---

## 📊 Database Management

### Connect to Database

```bash
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant
```

### Useful Queries

```sql
-- List all tenants
SELECT id, company_name, domain, status FROM tenants;

-- List all avatars
SELECT id, name, 
       CASE WHEN image_data IS NOT NULL THEN 'Has Image' ELSE 'No Image' END 
FROM avatars;

-- Update tenant domain
UPDATE tenants SET domain = 'localhost' WHERE company_name = 'Your Company';

-- Check avatar size
SELECT id, name, LENGTH(image_data) as size_bytes 
FROM avatars;
```

### Backup Database

```bash
# Backup
docker exec voice-agent-per_db-gpt-auido-mini-db-1 pg_dump -U postgres voice_agent_multi_tenant > backup.sql

# Restore
cat backup.sql | docker exec -i voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres voice_agent_multi_tenant
```

---

## 🔧 Docker Commands Reference

### Start/Stop

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

### Rebuild

```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild without cache
docker-compose build --no-cache
```

### Logs

```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Execute Commands

```bash
# Backend shell
docker exec -it voice-agent-per_db-gpt-auido-mini-backend-1 /bin/bash

# Database shell
docker exec -it voice-agent-per_db-gpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant

# Run Python script
docker exec voice-agent-per_db-gpt-auido-mini-backend-1 python script.py
```

---

## 🎯 Testing Workflow

### 1. Start Fresh

```bash
# Stop everything
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait for database
sleep 10
```

### 2. Create Test Data

```bash
# Open admin dashboard
# Create avatar
# Create tenant with domain = localhost
```

### 3. Test Widget

```bash
# Open CodelessAi.html in browser
# Should see avatar and hear introduction
```

### 4. Check Logs

```bash
# Backend logs
docker-compose logs backend | grep AUTH

# Should see:
# [AUTH] Success: Codeless AI
```

---

## 📦 What's Stored Where

| Data | Storage | Persistent? |
|------|---------|-------------|
| **Avatar Images** | PostgreSQL (base64) | ✅ Yes |
| **Tenant Config** | PostgreSQL | ✅ Yes |
| **Knowledge Base** | PostgreSQL | ✅ Yes |
| **Conversations** | PostgreSQL | ✅ Yes |
| **Backend Code** | Volume mount | ✅ Yes (on host) |
| **Database Data** | Docker volume | ✅ Yes |

---

## 🚀 Production Deployment

### 1. Remove Volume Mount

Edit `docker-compose.yml`:
```yaml
backend:
  build: ./backend
  # Remove this line in production:
  # volumes:
  #   - ./backend:/app
```

### 2. Use Environment File

Create `.env`:
```bash
ENCRYPTION_KEY=<generate-32-byte-key>
MASTER_ADMIN_SECRET=<strong-password>
DATABASE_URL=postgresql://user:pass@prod-db:5432/voice_agent
```

### 3. Deploy

```bash
# Build for production
docker-compose build

# Start
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

---

## ✅ Advantages of This Setup

1. **No File Management** - Images in database, not filesystem
2. **Live Updates** - Code changes apply instantly
3. **Easy Backup** - Just backup PostgreSQL
4. **Portable** - Works on any machine with Docker
5. **Isolated** - Each tenant's data separate
6. **Scalable** - Easy to add more backend containers

---

## 🎓 Key Concepts

### Base64 Image Storage

**Why?**
- No file system dependencies
- Survives container restarts
- Easy to backup with database
- No CDN needed for development

**Trade-offs:**
- Larger database size
- Slower for very large images
- Consider CDN for production

### Volume Mounting

**Development:**
```yaml
volumes:
  - ./backend:/app  # Live code updates
```

**Production:**
```yaml
# No volumes - code baked into image
```

### Docker Networking

Containers communicate via service names:
```python
DATABASE_URL=postgresql://postgres:postgres@db:5432/voice_agent
#                                            ↑
#                                      Service name
```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Logs | `docker-compose logs -f backend` |
| Database | `docker exec -it <db-container> psql -U postgres -d voice_agent_multi_tenant` |
| Rebuild | `docker-compose build backend` |
| Restart | `docker-compose restart backend` |
| Shell | `docker exec -it <backend-container> /bin/bash` |

---

**Ready to deploy!** 🚀
