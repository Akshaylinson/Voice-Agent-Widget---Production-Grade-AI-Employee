# Production Deployment Checklist

## 🚀 Pre-Production Changes Required

### 1. Environment Variables

**File: `backend/.env`**

```bash
# ❌ Development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voice_agent
OPENAI_API_KEY=sk-test-key
JWT_SECRET=dev-secret-123

# ✅ Production
DATABASE_URL=postgresql://user:password@prod-db-host:5432/voice_agent_prod
OPENAI_API_KEY=sk-prod-xxxxxxxxxxxxx
JWT_SECRET=<generate-strong-random-secret>
ENCRYPTION_KEY=<generate-32-byte-base64-key>
```

**Generate Secrets:**
```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key (32 bytes base64)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

### 2. Database Configuration

**Current (Development):**
- SQLite or local PostgreSQL
- No backups
- No replication

**Production Requirements:**
- ✅ Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database)
- ✅ Enable automated backups (daily minimum)
- ✅ Set up read replicas for scaling
- ✅ Configure connection pooling
- ✅ Enable SSL/TLS for database connections

**Update `backend/database.py`:**
```python
# Add SSL and connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},  # Force SSL
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

---

### 3. API URLs & Endpoints

**Files to Update:**
- `admin/index.html`
- `CodelessAi.html`
- `demo_acme.html`
- All client HTML files

**Change:**
```javascript
// ❌ Development
const API_URL = 'http://localhost:8000';
window.VOICE_AGENT_API_URL = "http://localhost:8000/api";

// ✅ Production
const API_URL = 'https://api.yourdomain.com';
window.VOICE_AGENT_API_URL = "https://api.yourdomain.com/api";
```

---

### 4. Widget Script URL

**Current (Development):**
```html
<script src="https://codeless-tcr.github.io/vvai/widget.js"></script>
```

**Production Options:**

**Option A: Self-hosted (Recommended)**
```html
<script src="https://cdn.yourdomain.com/widget.js"></script>
```

**Option B: Keep external CDN**
- Ensure CDN is reliable and versioned
- Consider hosting backup copy

---

### 5. CORS Configuration

**File: `backend/main.py`**

**Current (Development):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://admin.yourdomain.com",
        # Add all authorized client domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-Tenant-ID", "X-Signature"],
)
```

---

### 6. Domain Validation

**File: `backend/tenant_middleware.py`**

**Current:** Already configured to accept both localhost AND production domain ✅

**Verify tenant domains in database:**
```sql
-- Update all tenant domains to production URLs
UPDATE tenants SET domain = 'acmecorp.com' WHERE company_name = 'Acme Corp';
UPDATE tenants SET domain = 'codelessai.com' WHERE company_name = 'Codeless AI';
```

---

### 7. SSL/HTTPS Configuration

**Requirements:**
- ✅ All production URLs must use HTTPS
- ✅ Obtain SSL certificates (Let's Encrypt, AWS ACM, etc.)
- ✅ Configure reverse proxy (Nginx, Caddy, CloudFlare)
- ✅ Redirect HTTP to HTTPS
- ✅ Enable HSTS headers

**Nginx Example:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### 8. File Upload Configuration

**File: `backend/main.py`**

**Current:**
```python
UPLOADS_DIR = "uploads"  # Local directory
```

**Production (Use Cloud Storage):**
```python
# Option A: AWS S3
import boto3
s3_client = boto3.client('s3')
BUCKET_NAME = 'your-avatars-bucket'

# Option B: Google Cloud Storage
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket('your-avatars-bucket')

# Option C: Azure Blob Storage
from azure.storage.blob import BlobServiceClient
blob_service = BlobServiceClient.from_connection_string(conn_str)
```

**Update avatar URLs to use CDN:**
```python
# Instead of: http://localhost:8000/uploads/image.jpg
# Use: https://cdn.yourdomain.com/avatars/image.jpg
```

---

### 9. Logging & Monitoring

**File: `backend/main.py`**

**Current:**
```python
logging.basicConfig(level=logging.INFO)
```

**Production:**
```python
import logging
from logging.handlers import RotatingFileHandler

# File logging with rotation
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Add error tracking (Sentry, Rollbar, etc.)
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**Set up monitoring:**
- ✅ Application Performance Monitoring (APM)
- ✅ Error tracking (Sentry, Rollbar)
- ✅ Uptime monitoring (Pingdom, UptimeRobot)
- ✅ Log aggregation (CloudWatch, Datadog, ELK)

---

### 10. Rate Limiting

**Add to `backend/main.py`:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/voice-query")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def voice_query(request: Request, db: Session = Depends(get_db)):
    # ... existing code
```

---

### 11. Security Headers

**Add to `backend/main.py`:**

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Only allow specific hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.yourdomain.com", "*.yourdomain.com"]
)

# Add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

### 12. Docker Configuration

**File: `backend/Dockerfile`**

**Production optimizations:**
```dockerfile
FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Production server
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

**Update `requirements.txt`:**
```txt
gunicorn==21.2.0
uvicorn[standard]==0.24.0
```

---

### 13. Database Migrations

**Before deploying:**
```bash
# Backup production database
pg_dump -h prod-host -U user -d voice_agent_prod > backup_$(date +%Y%m%d).sql

# Test migrations on staging
alembic upgrade head

# Apply to production
alembic upgrade head
```

---

### 14. Admin Dashboard Security

**File: `admin/index.html`**

**Add authentication:**
```javascript
// Add login system
const ADMIN_PASSWORD = prompt("Enter admin password:");

fetch(`${API_URL}/admin/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({password: ADMIN_PASSWORD})
})
.then(res => res.json())
.then(data => {
    if (data.token) {
        localStorage.setItem('admin_token', data.token);
    }
});
```

**Backend: Add admin authentication endpoint**

---

### 15. Backup Strategy

**Automated backups:**
```bash
# Daily database backup
0 2 * * * pg_dump -h prod-host -U user voice_agent_prod | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Weekly full backup
0 3 * * 0 tar -czf /backups/full_$(date +\%Y\%m\%d).tar.gz /app /backups/db_*.sql.gz

# Retention: Keep 30 days
find /backups -name "*.gz" -mtime +30 -delete
```

---

### 16. Performance Optimization

**Enable caching:**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="voice-agent-cache")
```

**Database indexing:**
```sql
CREATE INDEX idx_tenant_domain ON tenants(domain);
CREATE INDEX idx_conversation_tenant ON conversations(tenant_id);
CREATE INDEX idx_knowledge_tenant ON knowledge_base(tenant_id);
```

---

### 17. CDN Configuration

**Static assets:**
- ✅ Serve widget.js from CDN
- ✅ Serve avatar images from CDN
- ✅ Enable gzip/brotli compression
- ✅ Set cache headers (1 year for immutable assets)

**CloudFlare/CloudFront settings:**
- Cache everything
- Browser cache TTL: 1 year
- Edge cache TTL: 1 month

---

### 18. Testing Checklist

**Before going live:**
- [ ] Test all API endpoints with production URLs
- [ ] Verify SSL certificates are valid
- [ ] Test widget on actual client domains
- [ ] Load testing (simulate 100+ concurrent users)
- [ ] Security scan (OWASP ZAP, Burp Suite)
- [ ] Verify database backups work
- [ ] Test disaster recovery procedure
- [ ] Check all error handling
- [ ] Verify logging is working
- [ ] Test rate limiting
- [ ] Verify CORS settings
- [ ] Test with real OpenAI API key
- [ ] Check billing/usage tracking

---

### 19. Deployment Steps

**Step-by-step:**

1. **Backup everything**
   ```bash
   pg_dump production_db > backup.sql
   tar -czf code_backup.tar.gz /app
   ```

2. **Update environment variables**
   - Set production DATABASE_URL
   - Set production API keys
   - Set strong secrets

3. **Deploy backend**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Run migrations**
   ```bash
   docker exec backend alembic upgrade head
   ```

5. **Update client HTML files**
   - Change all localhost URLs to production
   - Update widget script URLs

6. **Deploy admin dashboard**
   - Upload to hosting (Netlify, Vercel, S3)
   - Configure custom domain

7. **Update DNS records**
   - Point api.yourdomain.com to backend
   - Point admin.yourdomain.com to admin dashboard

8. **Test everything**
   - Create test tenant
   - Test widget on client site
   - Verify voice interactions work

9. **Monitor for 24 hours**
   - Check error logs
   - Monitor API response times
   - Watch database performance

---

### 20. Post-Deployment

**Ongoing maintenance:**
- [ ] Monitor error rates daily
- [ ] Review logs weekly
- [ ] Update dependencies monthly
- [ ] Security patches immediately
- [ ] Database optimization quarterly
- [ ] Backup verification monthly
- [ ] Load testing before major releases

---

## 🔒 Security Checklist

- [ ] All connections use HTTPS/SSL
- [ ] Database connections encrypted
- [ ] API keys stored encrypted
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Admin dashboard password protected
- [ ] Regular security audits

---

## 📊 Monitoring Checklist

- [ ] Application logs centralized
- [ ] Error tracking configured
- [ ] Uptime monitoring active
- [ ] Performance monitoring enabled
- [ ] Database monitoring setup
- [ ] Alerts configured for:
  - API errors > 1%
  - Response time > 2s
  - Database CPU > 80%
  - Disk space < 20%
  - Failed backups

---

## 💰 Cost Optimization

- [ ] Use reserved instances (AWS/GCP)
- [ ] Enable auto-scaling
- [ ] Optimize database queries
- [ ] Implement caching
- [ ] Compress responses
- [ ] Use CDN for static assets
- [ ] Monitor OpenAI API usage per tenant
- [ ] Set usage limits per tenant

---

## 📝 Documentation

**Update before launch:**
- [ ] API documentation
- [ ] Client integration guide
- [ ] Admin user manual
- [ ] Troubleshooting guide
- [ ] Disaster recovery plan
- [ ] Runbook for common issues

---

## Quick Reference

**Development → Production Changes:**

| Component | Development | Production |
|-----------|-------------|------------|
| API URL | http://localhost:8000 | https://api.yourdomain.com |
| Database | Local PostgreSQL | Managed PostgreSQL (RDS) |
| Storage | Local filesystem | S3/Cloud Storage |
| Logging | Console | File + Centralized |
| CORS | Allow all (*) | Specific domains only |
| SSL | Not required | Required (HTTPS) |
| Secrets | .env file | Environment variables |
| Monitoring | None | Full APM + alerts |
| Backups | Manual | Automated daily |
| Rate Limiting | Disabled | Enabled |

---

**Need Help?** Review each section carefully before deploying to production.
