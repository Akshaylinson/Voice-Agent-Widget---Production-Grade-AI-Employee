# 🚀 Quick Access Guide

## How to Access Each Page

### 1️⃣ Admin Dashboard (Master Admin)
**URL:** `http://localhost:3000`

**Purpose:** 
- Create and manage tenants
- Configure avatars and voices
- Manage knowledge base
- View analytics

**Requirements:**
- Docker containers must be running: `docker-compose up -d`

---

### 2️⃣ CodelessAi.html (Client Demo Page)
**URL:** `file:///e:/AI_INFLUC_ SAAS/voice-agent-per_db(gpt-auido-mini)/CodelessAi.html`

**Or via browser:**
1. Open your browser
2. Press `Ctrl + O` (or `Cmd + O` on Mac)
3. Navigate to: `e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)\CodelessAi.html`
4. Click "Open"

**Purpose:**
- Demo page for "Codeless AI" tenant
- Test voice assistant widget
- Shows sample questions and features

**Tenant ID:** `e78f6bbe-4cf0-471c-82cc-20f29a08506f`

---

### 3️⃣ demo_acme.html (Client Demo Page)
**URL:** `file:///e:/AI_INFLUC_ SAAS/voice-agent-per_db(gpt-auido-mini)/demo_acme.html`

**Or via browser:**
1. Open your browser
2. Press `Ctrl + O` (or `Cmd + O` on Mac)
3. Navigate to: `e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)\demo_acme.html`
4. Click "Open"

**Purpose:**
- Demo page for "Acme Corp" tenant
- Test voice assistant widget
- Shows sample questions and features

**Tenant ID:** `8f06cdd9-bac4-4184-987f-f5c8fc63b8b0`

---

## 🔧 Prerequisites

### Start the System:
```bash
# Navigate to project directory
cd "e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)"

# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps
```

### Verify Services:
- **Backend API:** `http://localhost:8000/health`
- **Admin Dashboard:** `http://localhost:3000`
- **Database:** `localhost:5432`

---

## 📋 Quick Access Summary

| Page | URL | Port | Purpose |
|------|-----|------|---------|
| **Admin Dashboard** | http://localhost:3000 | 3000 | Manage tenants & config |
| **Backend API** | http://localhost:8000 | 8000 | API endpoints |
| **CodelessAi Demo** | Open file directly | - | Test Codeless AI widget |
| **Acme Demo** | Open file directly | - | Test Acme Corp widget |

---

## 🎯 Testing Workflow

1. **Start Docker:** `docker-compose up -d`
2. **Open Admin:** http://localhost:3000
3. **Configure Tenant:** Add knowledge, set avatar, etc.
4. **Open Demo Page:** CodelessAi.html or demo_acme.html
5. **Test Widget:** Click avatar, speak to AI assistant

---

## 🐛 Troubleshooting

### Admin Dashboard Not Loading:
```bash
docker-compose logs admin
```

### Backend API Not Responding:
```bash
docker-compose logs backend
```

### Widget Not Working:
- Check browser console (F12)
- Verify backend is running: http://localhost:8000/health
- Ensure microphone permissions are granted

### Database Issues:
```bash
docker-compose logs db
```

---

## 💡 Pro Tips

- **Browser Console:** Press F12 to see widget logs
- **Live Reload:** Backend code changes auto-reload
- **Multiple Tenants:** Each tenant has unique ID and signature
- **HTTPS Required:** For production, use HTTPS for microphone access
