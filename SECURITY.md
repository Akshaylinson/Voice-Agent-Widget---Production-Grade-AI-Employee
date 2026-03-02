# 🔐 Environment Configuration & Security Guide

## Overview

The Voice Agent backend uses environment-based configuration to securely manage all API keys, credentials, and sensitive settings. **No secrets are hardcoded in source code.**

## Required Environment Variables

### API Keys (REQUIRED)

```bash
# OpenRouter API Key for GPT Audio Mini voice processing
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# JWT Secret for authentication (minimum 16 characters)
JWT_SECRET=your-secure-random-string-here
```

### Database Configuration

```bash
# PostgreSQL connection string
DATABASE_URL=postgresql://postgres:postgres@db-client1:5432/voice_agent

# Unique client identifier
CLIENT_ID=client1
```

### Voice Model Configuration

```bash
# Voice model identifier (default: openai/gpt-4o-audio-preview)
VOICE_MODEL_ID=openai/gpt-4o-audio-preview

# Model provider (default: openrouter)
VOICE_MODEL_PROVIDER=openrouter
```

### Service Configuration (Optional)

```bash
# API request timeout in seconds (default: 60)
API_TIMEOUT=60

# Maximum audio file size in MB (default: 25)
MAX_AUDIO_SIZE_MB=25

# Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
LOG_LEVEL=INFO

# Log API requests for debugging (default: false)
LOG_API_REQUESTS=false

# CORS allowed origins, comma-separated (default: *)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Setup Instructions

### 1. Local Development

```bash
# Copy template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

**Example `.env` file:**
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
JWT_SECRET=my-super-secure-secret-key-123456
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voice_agent
CLIENT_ID=dev_client
VOICE_MODEL_ID=openai/gpt-4o-audio-preview
LOG_LEVEL=DEBUG
LOG_API_REQUESTS=true
```

### 2. Docker Deployment

Environment variables are automatically loaded from `.env` file:

```bash
docker-compose up -d
```

### 3. Production Deployment

**Option A: Environment File**
```bash
docker run -d \
  --env-file .env \
  voice-agent:latest
```

**Option B: Direct Environment Variables**
```bash
docker run -d \
  -e OPENROUTER_API_KEY=sk-or-v1-xxx \
  -e JWT_SECRET=secure-secret \
  -e DATABASE_URL=postgresql://... \
  -e CLIENT_ID=client1 \
  voice-agent:latest
```

**Option C: Kubernetes Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: voice-agent-secrets
type: Opaque
stringData:
  openrouter-api-key: sk-or-v1-xxxxxxxxxxxxx
  jwt-secret: your-secure-secret
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: voice-agent
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: voice-agent-secrets
              key: openrouter-api-key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: voice-agent-secrets
              key: jwt-secret
```

## Security Best Practices

### ✅ DO

- Store `.env` file outside version control
- Use strong, random JWT secrets (32+ characters)
- Rotate API keys regularly
- Use different secrets per environment (dev/staging/prod)
- Restrict CORS origins in production
- Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
- Set `LOG_API_REQUESTS=false` in production
- Use HTTPS in production

### ❌ DON'T

- Commit `.env` file to Git
- Hardcode API keys in source code
- Share API keys in chat/email
- Use default/example secrets in production
- Log API keys or secrets
- Expose secrets in frontend code
- Use same secrets across environments

## Configuration Validation

The backend validates all required environment variables on startup:

```python
# Automatic validation on startup
from config import settings

# If validation fails, the application exits with error:
# ❌ Configuration Error: OPENROUTER_API_KEY must be set to a valid API key
```

**Validation checks:**
- ✅ OPENROUTER_API_KEY is present and not placeholder
- ✅ JWT_SECRET is at least 16 characters
- ✅ DATABASE_URL is valid PostgreSQL connection string
- ✅ CLIENT_ID is set

## Getting OpenRouter API Key

1. Visit: https://openrouter.ai/
2. Sign up for an account
3. Navigate to API Keys section
4. Create new API key
5. Copy key (starts with `sk-or-v1-`)
6. Add to `.env` file

## Accessing Configuration in Code

**Centralized configuration access:**

```python
from config import settings

# Access API key
api_key = settings.openrouter_api_key

# Access voice model
model_id = settings.voice_model_id

# Access timeout
timeout = settings.api_timeout
```

**Never access environment variables directly:**
```python
# ❌ BAD - Don't do this
import os
api_key = os.getenv("OPENROUTER_API_KEY")

# ✅ GOOD - Use centralized config
from config import settings
api_key = settings.openrouter_api_key
```

## Troubleshooting

### Error: "OPENROUTER_API_KEY must be set"

**Solution:**
1. Check `.env` file exists in backend directory
2. Verify API key is set correctly
3. Ensure no spaces around `=` sign
4. Restart application

### Error: "JWT_SECRET must be at least 16 characters"

**Solution:**
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
JWT_SECRET=generated-secret-here
```

### Error: Configuration not loading

**Solution:**
```bash
# Check .env file location
ls -la .env

# Verify file encoding (must be UTF-8)
file .env

# Check for syntax errors
cat .env | grep -v '^#' | grep -v '^$'
```

## Environment Variable Precedence

1. **System environment variables** (highest priority)
2. **Docker environment variables**
3. **`.env` file**
4. **Default values** (lowest priority)

## Monitoring & Logging

**Safe logging (secrets are never logged):**

```python
# ✅ Safe - logs model ID, not API key
logger.info(f"Using voice model: {settings.voice_model_id}")

# ✅ Safe - logs client ID
logger.info(f"Client: {settings.client_id}")

# ❌ Never log secrets
# logger.info(f"API Key: {settings.openrouter_api_key}")  # DON'T DO THIS
```

## Multi-Environment Setup

**Development:**
```bash
# .env.development
OPENROUTER_API_KEY=sk-or-v1-dev-key
LOG_LEVEL=DEBUG
LOG_API_REQUESTS=true
```

**Production:**
```bash
# .env.production
OPENROUTER_API_KEY=sk-or-v1-prod-key
LOG_LEVEL=WARNING
LOG_API_REQUESTS=false
CORS_ORIGINS=https://yourdomain.com
```

**Load specific environment:**
```bash
# Development
cp .env.development .env
docker-compose up -d

# Production
cp .env.production .env
docker-compose up -d
```

## Security Checklist

- [ ] `.env` file added to `.gitignore`
- [ ] OpenRouter API key obtained and configured
- [ ] JWT secret generated (32+ characters)
- [ ] Different secrets for dev/staging/prod
- [ ] CORS origins restricted in production
- [ ] API request logging disabled in production
- [ ] Secrets stored in secure vault (production)
- [ ] Regular API key rotation scheduled
- [ ] Team members trained on secret handling
- [ ] Monitoring alerts configured

## Support

For security concerns or questions:
- Review this documentation
- Check application logs
- Verify environment variable values (without exposing secrets)
- Test with minimal configuration first

---

**Remember: Never commit secrets to version control. Always use environment variables.**
