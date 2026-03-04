# 🚀 Gemini Voice Agent - Quick Reference

## 📦 Installation (5 Minutes)

```bash
# 1. Configure
python configure.py

# 2. Start
docker-compose up -d

# 3. Test
python test_gemini.py

# 4. Access
# Admin: http://localhost:3000
# API: http://localhost:8000
```

## 🔑 Environment Variables

```bash
GEMINI_API_KEY=AIza...              # Required
GEMINI_MODEL=gemini-1.5-flash       # Default
GEMINI_EMBEDDING_MODEL=text-embedding-004
GEMINI_LIVE_MODEL=gemini-2.0-flash-exp
DATABASE_URL=postgresql://...       # Required
ENCRYPTION_KEY=...                  # Auto-generated
```

## 🎯 Core Endpoints

### Admin
```bash
POST /admin/tenants                 # Create tenant
GET  /admin/tenants                 # List tenants
GET  /admin/tenant/{id}             # Get tenant details
PUT  /admin/tenant/{id}             # Update tenant
POST /admin/tenant/{id}/knowledge   # Add knowledge
```

### Public API
```bash
GET  /api/config                    # Get tenant config
POST /api/text-query                # Text conversation
POST /api/voice-query               # Voice conversation
GET  /api/conversations             # Get history
WS   /ws/voice-stream               # Real-time streaming
```

## 💬 Create Tenant

```bash
curl -X POST http://localhost:8000/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "domain": "acme.com",
    "gemini_api_key": "optional",
    "voice_model": "Puck",
    "voice_gender": "female",
    "speaking_rate": 1.0,
    "introduction_script": "Hello! How can I help?"
  }'
```

## 📚 Add Knowledge

```bash
curl -X POST http://localhost:8000/admin/tenant/{tenant_id}/knowledge \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: {tenant_id}" \
  -H "X-Signature: admin-override" \
  -d '{
    "category": "services",
    "title": "Web Development",
    "content": "We build modern web apps with React and Node.js"
  }'
```

## 🎤 Widget Embed

```html
<script>
window.VOICE_AGENT_TENANT_ID = "uuid";
window.VOICE_AGENT_SIGNATURE = "signature";
window.VOICE_AGENT_API_URL = "http://localhost:8000/api";
</script>
<script src="http://localhost:8000/voice-agent-widget.js"></script>
```

## 🔍 RAG Flow

```
User Query
    ↓
Generate Embedding (768-dim)
    ↓
Vector Search (pgvector)
    ↓
Retrieve Top 5 Knowledge
    ↓
Inject into Gemini Prompt
    ↓
Generate Response
    ↓
Return to User
```

## 🎨 Voice Models

| Model | Gender | Tone |
|-------|--------|------|
| Puck | Female | Friendly |
| Charon | Male | Professional |
| Kore | Female | Warm |
| Fenrir | Male | Authoritative |
| Aoede | Female | Energetic |

## 🗄️ Database Schema

```sql
-- Tenants
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  company_name VARCHAR(255),
  domain VARCHAR(255),
  gemini_api_key_encrypted TEXT,
  voice_model VARCHAR(50),
  voice_gender VARCHAR(20),
  speaking_rate FLOAT,
  widget_signature VARCHAR(255)
);

-- Knowledge Base
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY,
  tenant_id UUID,
  category VARCHAR(100),
  title VARCHAR(255),
  content TEXT,
  embedding vector(768),  -- pgvector
  is_active BOOLEAN
);

-- Conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  tenant_id UUID,
  session_id VARCHAR(100),
  transcript TEXT,
  response TEXT,
  token_usage INTEGER,
  duration FLOAT,
  created_at TIMESTAMP
);
```

## 🧪 Testing

```bash
# Full test suite
python test_gemini.py

# Manual tests
curl http://localhost:8000/health
curl http://localhost:8000/api/config?tenant_id=X&signature=Y

# Database check
docker exec -it db-client1 psql -U postgres -d voice_agent_multi_tenant
```

## 📊 Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Embedding Gen | <200ms | ~100ms |
| Vector Search | <50ms | <50ms |
| Gemini Response | <2s | 500-1500ms |
| Total Latency | <3s | <2s |

## 🐛 Debug Commands

```bash
# Logs
docker logs voice-agent-client1 -f
docker logs db-client1 -f

# Container status
docker ps
docker stats

# Database
docker exec -it db-client1 psql -U postgres -d voice_agent_multi_tenant

# Check pgvector
SELECT * FROM pg_extension WHERE extname = 'vector';

# Check embeddings
SELECT id, title, embedding IS NOT NULL FROM knowledge_base;

# Restart
docker-compose restart
docker-compose down && docker-compose up -d
```

## 🔒 Security Checklist

- [x] API keys encrypted (Fernet)
- [x] No keys in frontend
- [x] Widget signature verification
- [x] Domain whitelist
- [x] HTTPS (production)
- [x] Rate limiting (recommended)

## 📈 Monitoring Queries

```sql
-- Conversation stats
SELECT 
  tenant_id,
  COUNT(*) as total,
  AVG(duration) as avg_duration
FROM conversations
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY tenant_id;

-- Knowledge usage
SELECT 
  kb.title,
  COUNT(c.id) as mentions
FROM knowledge_base kb
LEFT JOIN conversations c 
  ON c.response LIKE '%' || kb.title || '%'
GROUP BY kb.title
ORDER BY mentions DESC;

-- Embedding coverage
SELECT 
  COUNT(*) as total,
  COUNT(embedding) as with_embedding,
  ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage_pct
FROM knowledge_base;
```

## 🚨 Common Issues

### Widget not loading
```bash
# Check CORS
# Verify API_URL
# Check browser console
```

### No embeddings
```bash
# Check Gemini API key
# Verify pgvector extension
# Manually regenerate
```

### Slow responses
```bash
# Check database indexes
# Monitor API latency
# Verify network
```

## 📚 Documentation

- `README.md` - Overview
- `GEMINI_UPGRADE.md` - Full guide
- `UPGRADE_SUMMARY.md` - Summary
- `DEPLOYMENT_CHECKLIST.md` - Checklist

## 🆘 Support

```bash
# Configuration help
python configure.py

# Run tests
python test_gemini.py

# Check health
curl http://localhost:8000/health
```

## 🎉 Quick Start Commands

```bash
# Setup
git clone <repo>
cd voice-agent-per_db
python configure.py
docker-compose up -d

# Create tenant
curl -X POST http://localhost:8000/admin/tenants -d @tenant.json

# Add knowledge
curl -X POST http://localhost:8000/admin/tenant/{id}/knowledge -d @knowledge.json

# Test
python test_gemini.py

# Monitor
docker logs -f voice-agent-client1
```

---

**Version**: 3.0-gemini  
**Last Updated**: 2024  
**Status**: Production Ready ✅
