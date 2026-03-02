# 🧪 Testing & Troubleshooting Guide

## Quick Test Checklist

- [ ] Docker containers running
- [ ] Database initialized
- [ ] OpenAI API key configured
- [ ] Admin dashboard accessible
- [ ] Configuration saved
- [ ] Knowledge entries added
- [ ] Widget loads on demo page
- [ ] Microphone permission granted
- [ ] Introduction plays
- [ ] Voice query processed
- [ ] Response received
- [ ] Conversation logged

## Testing Workflow

### 1. Verify Deployment

```bash
# Check running containers
docker ps

# Expected output:
# voice-agent-client1 (running)
# db-client1 (running)
# admin-dashboard (running)

# Check container logs
docker logs voice-agent-client1
docker logs db-client1

# Test health endpoint
curl http://localhost:8001/health
# Expected: {"status":"healthy","client_id":"client1"}
```

### 2. Test Admin Dashboard

**Access**: http://localhost:3000

**Configuration Tab:**
1. Enter company name: "Test Company"
2. Add avatar URL (optional)
3. Set introduction: "Hello! I'm your test AI assistant. How can I help?"
4. Select voice: "alloy"
5. Click "Save Configuration"
6. Verify success message

**Knowledge Tab:**
1. Add test entry:
   - Category: services
   - Title: "Web Development"
   - Content: "We offer professional web development services including React, Node.js, and cloud deployment."
2. Click "Add Knowledge"
3. Verify entry appears in table

**Conversations Tab:**
1. Should be empty initially
2. Will populate after widget interactions

### 3. Test API Endpoints

```bash
# Get configuration
curl http://localhost:8001/api/config

# Get introduction audio
curl http://localhost:8001/api/introduction -o intro.mp3

# List knowledge
curl http://localhost:8001/api/knowledge

# Add knowledge via API
curl -X POST http://localhost:8001/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "category": "faq",
    "title": "Business Hours",
    "content": "We are open Monday to Friday, 9 AM to 6 PM EST."
  }'

# Get conversations
curl http://localhost:8001/api/conversations
```

### 4. Test Widget Integration

**Open demo.html in browser**

**Test Sequence:**
1. Page loads with floating avatar visible
2. Click avatar
3. Browser requests microphone permission → Allow
4. Introduction audio plays automatically
5. After introduction, recording starts (red indicator)
6. Speak: "What services do you offer?"
7. Recording stops after silence
8. Processing indicator (optional)
9. Response plays automatically
10. Returns to listening state
11. Click avatar again to deactivate

**Expected Behavior:**
- Avatar pulses during listening
- Avatar animates during speaking
- Status indicator changes color
- Smooth audio playback
- No console errors

### 5. Test Voice Queries

**Test Questions:**

**Basic Information:**
- "What services do you offer?"
- "Tell me about your company"
- "What are your business hours?"

**Pricing:**
- "How much does it cost?"
- "What are your pricing plans?"
- "Do you offer discounts?"

**Contact:**
- "How can I contact you?"
- "What's your email address?"
- "Where are you located?"

**Out of Scope:**
- "What's the weather today?" (should say no info available)
- "Tell me a joke" (should redirect to company topics)

**Expected Responses:**
- Concise (30-60 seconds)
- Voice-optimized language
- Based on knowledge base
- Offers follow-up if needed
- Graceful handling of unknown topics

### 6. Test Multi-Language (if configured)

```bash
# Update config for Spanish
curl -X POST http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "supported_languages": ["en", "es"]
  }'

# Test Spanish query
# Speak: "¿Qué servicios ofrecen?"
```

### 7. Test Session Continuity

1. Click avatar, ask: "What services do you offer?"
2. Wait for response
3. Ask follow-up: "How much does that cost?"
4. Verify context is maintained via session_id

### 8. Test Mobile Responsiveness

**On Mobile Device:**
1. Open demo.html on phone
2. Verify avatar size appropriate
3. Test touch interaction
4. Verify microphone access
5. Test audio playback
6. Check positioning (bottom-right)

### 9. Test Error Handling

**No Microphone:**
- Deny microphone permission
- Expected: Alert message

**No Internet:**
- Disconnect network
- Expected: Graceful error, retry option

**Invalid Audio:**
- Send corrupted audio file
- Expected: Error handling, user notification

**Empty Knowledge Base:**
- Remove all knowledge entries
- Ask question
- Expected: "I don't have that information" response

### 10. Performance Testing

```bash
# Test response time
time curl http://localhost:8001/api/config

# Load test (requires Apache Bench)
ab -n 100 -c 10 http://localhost:8001/health

# Monitor container resources
docker stats voice-agent-client1
```

## Troubleshooting Guide

### Issue: Containers Won't Start

**Symptoms:**
- `docker ps` shows no containers
- Error messages during `docker-compose up`

**Solutions:**
```bash
# Check Docker is running
docker --version

# Check for port conflicts
netstat -ano | findstr :8001
netstat -ano | findstr :5432

# Remove old containers
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs
```

### Issue: Database Connection Failed

**Symptoms:**
- Backend logs show "connection refused"
- API returns 500 errors

**Solutions:**
```bash
# Check database container
docker logs db-client1

# Verify database is ready
docker exec -it db-client1 psql -U postgres -d voice_agent -c "SELECT 1;"

# Wait for database initialization (30 seconds)
sleep 30

# Restart backend
docker restart voice-agent-client1

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Issue: Widget Not Loading

**Symptoms:**
- Avatar doesn't appear on page
- Console shows 404 or CORS errors

**Solutions:**
```javascript
// Check browser console (F12)
// Look for errors

// Verify API URL is correct
console.log(window.VOICE_AGENT_API_URL);

// Test widget file directly
// Open: http://localhost:8001/voice-agent-widget.js

// Check CORS headers
fetch('http://localhost:8001/api/config')
  .then(r => console.log(r.headers.get('access-control-allow-origin')))
  .catch(e => console.error(e));
```

**Fix CORS:**
```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Microphone Not Working

**Symptoms:**
- Permission denied
- No audio captured
- Silent recording

**Solutions:**
1. **Use HTTPS**: Microphone requires secure context
   - Use localhost (allowed)
   - Or deploy with SSL certificate

2. **Check Browser Permissions:**
   - Chrome: Settings → Privacy → Site Settings → Microphone
   - Firefox: Preferences → Privacy → Permissions → Microphone
   - Allow for your domain

3. **Test Microphone:**
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => console.log('Microphone working!'))
  .catch(err => console.error('Microphone error:', err));
```

4. **Check Browser Support:**
```javascript
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
  console.error('Browser does not support microphone access');
}
```

### Issue: No Audio Playback

**Symptoms:**
- Response received but no sound
- Audio element not playing

**Solutions:**
```javascript
// Check audio support
const audio = new Audio();
console.log('Can play MP3:', audio.canPlayType('audio/mpeg'));

// Test audio playback
const testAudio = new Audio('http://localhost:8001/api/introduction');
testAudio.play()
  .then(() => console.log('Audio playing'))
  .catch(err => console.error('Playback error:', err));

// Check browser autoplay policy
// User interaction required before audio plays
```

### Issue: OpenAI API Errors

**Symptoms:**
- 401 Unauthorized
- 429 Rate limit exceeded
- 500 Internal server error

**Solutions:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check OpenAI status
# Visit: https://status.openai.com

# Check rate limits in OpenAI dashboard
# Visit: https://platform.openai.com/account/rate-limits

# Increase timeout in voice_service.py
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60)
```

### Issue: Slow Response Times

**Symptoms:**
- Long wait between query and response
- Timeout errors

**Solutions:**
```bash
# Check OpenAI API latency
time curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Monitor container resources
docker stats voice-agent-client1

# Increase container resources in docker-compose.yml
services:
  voice-agent-client1:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

# Optimize knowledge retrieval
# Add database indexes
CREATE INDEX idx_client_knowledge ON company_knowledge(client_id, is_active);

# Reduce response length
# In voice_service.py, adjust max_tokens
max_tokens=100  # Shorter responses
```

### Issue: Introduction Not Playing

**Symptoms:**
- Widget activates but no audio
- 404 error for introduction endpoint

**Solutions:**
```bash
# Check introduction is configured
curl http://localhost:8001/api/config | grep introduction_script

# Test introduction endpoint
curl http://localhost:8001/api/introduction -o test.mp3

# Play test file
# Windows: start test.mp3
# Mac: open test.mp3
# Linux: xdg-open test.mp3

# Update introduction in admin dashboard
# Or via API:
curl -X POST http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "introduction_script": "Hello! I am your AI assistant."
  }'
```

### Issue: Knowledge Not Retrieved

**Symptoms:**
- Agent says "I don't have that information"
- Responses don't match knowledge base

**Solutions:**
```bash
# Verify knowledge entries exist
curl http://localhost:8001/api/knowledge

# Check client_id matches
docker exec -it db-client1 psql -U postgres -d voice_agent \
  -c "SELECT client_id, title FROM company_knowledge;"

# Verify is_active flag
docker exec -it db-client1 psql -U postgres -d voice_agent \
  -c "SELECT * FROM company_knowledge WHERE is_active = false;"

# Add more detailed knowledge
# Be specific and comprehensive in content
```

### Issue: Conversations Not Logging

**Symptoms:**
- Conversations tab empty
- No records in database

**Solutions:**
```bash
# Check database connection
docker exec -it db-client1 psql -U postgres -d voice_agent \
  -c "SELECT COUNT(*) FROM conversations;"

# Verify table exists
docker exec -it db-client1 psql -U postgres -d voice_agent \
  -c "\dt"

# Check backend logs for errors
docker logs voice-agent-client1 | grep -i error

# Manually test conversation logging
curl -X POST http://localhost:8001/api/voice-query \
  -F "audio=@test.webm"
```

## Debugging Tools

### Browser DevTools

**Console (F12):**
```javascript
// Check widget loaded
console.log(document.getElementById('voice-agent-root'));

// Check API URL
console.log(window.VOICE_AGENT_API_URL);

// Test API connection
fetch(window.VOICE_AGENT_API_URL + '/config')
  .then(r => r.json())
  .then(d => console.log(d));

// Monitor audio events
const audio = new Audio();
audio.addEventListener('play', () => console.log('Audio started'));
audio.addEventListener('ended', () => console.log('Audio ended'));
audio.addEventListener('error', (e) => console.error('Audio error:', e));
```

**Network Tab:**
- Monitor API requests
- Check response times
- Verify CORS headers
- Inspect audio file sizes

### Docker Debugging

```bash
# Enter container shell
docker exec -it voice-agent-client1 /bin/bash

# Check Python environment
python --version
pip list

# Test database connection from container
python -c "from database import engine; print(engine.connect())"

# View environment variables
docker exec voice-agent-client1 env

# Check file system
docker exec voice-agent-client1 ls -la /app
```

### Database Debugging

```bash
# Connect to database
docker exec -it db-client1 psql -U postgres -d voice_agent

# List tables
\dt

# Check table structure
\d client_config
\d company_knowledge
\d conversations

# Query data
SELECT * FROM client_config;
SELECT client_id, title FROM company_knowledge;
SELECT COUNT(*) FROM conversations;

# Check indexes
\di

# Exit
\q
```

## Performance Benchmarks

### Expected Metrics

**API Response Times:**
- GET /config: < 50ms
- GET /introduction: < 2s
- POST /voice-query: 3-8s (depends on audio length)
- GET /knowledge: < 100ms

**Voice Processing:**
- Whisper transcription: 1-3s
- GPT response generation: 1-2s
- TTS synthesis: 1-3s
- Total: 3-8s per query

**Resource Usage:**
- Backend container: 200-500MB RAM
- Database container: 50-100MB RAM
- CPU: < 20% during idle, 50-80% during processing

## Load Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Mac: brew install httpd
# Linux: apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8001/health

# Test config endpoint
ab -n 100 -c 5 http://localhost:8001/api/config

# Expected results:
# - 99% requests < 100ms
# - 0% failed requests
# - Throughput > 100 req/sec
```

## Security Testing

```bash
# Test CORS
curl -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8001/api/config

# Test SQL injection (should be protected)
curl "http://localhost:8001/api/knowledge?client_id='; DROP TABLE conversations; --"

# Test file upload limits
# Create large file (> 10MB)
dd if=/dev/zero of=large.webm bs=1M count=20
curl -X POST http://localhost:8001/api/voice-query -F "audio=@large.webm"
```

## Automated Testing Script

```bash
#!/bin/bash
# test-voice-agent.sh

echo "🧪 Testing Voice Agent System..."

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -f http://localhost:8001/health || exit 1
echo "✅ Health check passed"

# Test 2: Configuration
echo "2. Testing configuration..."
curl -f http://localhost:8001/api/config || exit 1
echo "✅ Configuration passed"

# Test 3: Knowledge
echo "3. Testing knowledge endpoint..."
curl -f http://localhost:8001/api/knowledge || exit 1
echo "✅ Knowledge passed"

# Test 4: Widget file
echo "4. Testing widget file..."
curl -f http://localhost:8001/voice-agent-widget.js || exit 1
echo "✅ Widget file passed"

echo "🎉 All tests passed!"
```

## Support Checklist

When reporting issues, provide:
- [ ] Docker version: `docker --version`
- [ ] Container status: `docker ps`
- [ ] Backend logs: `docker logs voice-agent-client1`
- [ ] Database logs: `docker logs db-client1`
- [ ] Browser console errors (screenshot)
- [ ] Network tab (screenshot)
- [ ] Configuration: `curl http://localhost:8001/api/config`
- [ ] Knowledge count: `curl http://localhost:8001/api/knowledge | jq length`
- [ ] OpenAI API status: https://status.openai.com

---

**For additional support, refer to:**
- README.md - Complete documentation
- QUICKSTART.md - Setup guide
- API.md - API reference
- PRODUCTION.md - Deployment guide
