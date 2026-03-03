# OpenRouter TTS Implementation - Complete Summary

## ✅ What Was Implemented

### Architecture
```
Browser Web Speech API (STT)
    ↓ transcript text
Backend OpenRouter GPT-4o-mini (LLM)
    ↓ response text
Backend OpenRouter GPT-4o Audio Preview (TTS)
    ↓ audio bytes (mp3)
Browser Audio Player
```

---

## 📁 Files Updated

### 1. `.env`
```env
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_TTS_MODEL=openai/gpt-4o-audio-preview
OPENROUTER_HTTP_REFERER=http://localhost:8000
OPENROUTER_APP_TITLE=Codeless AI Voice Platform
```

### 2. `backend/openai_service.py`
- `generate_response()` - Uses OpenRouter GPT-4o-mini for text generation
- `text_to_speech()` - Uses OpenRouter GPT-4o Audio Preview for TTS
- Proper headers: Authorization, HTTP-Referer, X-Title
- Base64 audio decoding
- Error handling

### 3. `backend/main.py`
- `/api/introduction` - Returns audio stream (not JSON)
- `/api/voice-query` - Accepts transcript, returns audio stream
- Multi-tenant API key support (tenant key or master key)
- StreamingResponse for audio
- Proper error handling

---

## 🔑 Key Features

### 1. Multi-Tenant API Keys
```python
# Use tenant-specific key if available, else master key
api_key = tenant.decrypted_api_key or os.getenv("OPENROUTER_API_KEY")
```

### 2. Natural Voice Quality
- Uses OpenRouter GPT-4o Audio Preview
- Much better than browser TTS
- Consistent across all browsers
- 6 voice options: alloy, echo, fable, onyx, nova, shimmer

### 3. Streaming Audio Response
```python
return StreamingResponse(
    io.BytesIO(audio_bytes),
    media_type="audio/mpeg"
)
```

### 4. Browser STT Integration
- Widget uses Web Speech API for transcription
- Sends text to backend (not audio file)
- Faster and more efficient

---

## 🎯 API Endpoints

### GET /api/introduction
**Request:**
```
Headers:
  X-Tenant-ID: uuid
  X-Signature: hash
```

**Response:**
```
Content-Type: audio/mpeg
Body: <audio bytes>
```

### POST /api/voice-query
**Request:**
```
Headers:
  X-Tenant-ID: uuid
  X-Signature: hash

Body (FormData):
  transcript: "What services do you offer?"
  session_id: "uuid"
```

**Response:**
```
Content-Type: audio/mpeg
Headers:
  X-Session-ID: uuid
Body: <audio bytes>
```

---

## 🔧 Widget Integration

### Send Query
```javascript
const formData = new FormData();
formData.append('transcript', transcript);
formData.append('session_id', sessionId);

const response = await fetch(`${API_URL}/voice-query`, {
    method: 'POST',
    headers: {
        'X-Tenant-ID': TENANT_ID,
        'X-Signature': SIGNATURE
    },
    body: formData
});

const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
await audio.play();
```

---

## 💰 Cost Analysis

### OpenRouter Pricing
- **GPT-4o-mini (Text):** $0.15 input + $0.60 output per 1M tokens
- **GPT-4o Audio (TTS):** $2.50 input + $100 output per 1M tokens

### Example Calculation
100 conversations × 50 words × 1.5 tokens/word = 7,500 tokens

**Text Generation:**
- Input: 7,500 tokens × $0.15/1M = $0.001
- Output: 7,500 tokens × $0.60/1M = $0.005
- Total: $0.006

**TTS Generation:**
- Input: 7,500 tokens × $2.50/1M = $0.019
- Output: 7,500 tokens × $100/1M = $0.750
- Total: $0.769

**Total per 100 conversations: ~$0.78**
**Per conversation: ~$0.008**

---

## 🚀 Deployment Steps

### 1. Get OpenRouter API Key
```bash
# Visit https://openrouter.ai/
# Sign up and create API key
```

### 2. Update Environment
```bash
# Edit .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### 3. Restart Backend
```bash
# Docker
docker-compose restart backend

# Local
uvicorn main:app --reload
```

### 4. Update Widget
```javascript
// Widget should send transcript, not audio
// Widget should play audio blob response
```

### 5. Test
```bash
# Test introduction
curl -H "X-Tenant-ID: xxx" -H "X-Signature: xxx" \
  http://localhost:8000/api/introduction --output intro.mp3

# Test voice query
curl -X POST -H "X-Tenant-ID: xxx" -H "X-Signature: xxx" \
  -F "transcript=Hello" \
  http://localhost:8000/api/voice-query --output response.mp3
```

---

## ✅ Advantages

| Feature | Before (Browser TTS) | After (OpenRouter) |
|---------|---------------------|-------------------|
| Voice Quality | ⭐⭐ Robotic | ⭐⭐⭐⭐⭐ Natural |
| Consistency | Varies by browser | Always same |
| Customization | Limited | Full control |
| Languages | Browser-dependent | Consistent |
| Cost | Free | ~$0.008/conversation |

---

## 🔒 Security

### API Key Protection
- ✅ Never exposed to frontend
- ✅ Stored encrypted in database
- ✅ Backend-only access
- ✅ Per-tenant isolation

### Request Validation
- ✅ Tenant ID verification
- ✅ Signature validation
- ✅ Domain authorization
- ✅ Rate limiting (recommended)

---

## 📊 Monitoring

### Backend Logs
```
[LLM] Generating response for: What services...
[LLM] Response generated: We offer...
[TTS] Converting text to speech: We offer...
[TTS] Audio generated: 45678 bytes
```

### OpenRouter Dashboard
- Track API usage
- Monitor costs
- View request logs
- Set spending limits

---

## 🐛 Troubleshooting

### Issue: No audio returned
**Solution:**
1. Check OpenRouter API key is valid
2. Verify model name: `openai/gpt-4o-audio-preview`
3. Check backend logs for errors
4. Test with curl command

### Issue: Audio doesn't play
**Solution:**
1. Check browser console
2. Verify Content-Type: audio/mpeg
3. Check audio blob size > 0
4. Test audio file directly

### Issue: Poor voice quality
**Solution:**
1. Try different voice model
2. Add punctuation to text
3. Use shorter sentences
4. Check audio format

---

## 📚 Documentation Files

1. **WIDGET_OPENROUTER_TTS.md** - Widget integration guide
2. **OPENROUTER_TTS_SUMMARY.md** - This file
3. **.env** - Environment configuration
4. **backend/openai_service.py** - TTS implementation
5. **backend/main.py** - API endpoints

---

## 🎓 Next Steps

1. **Get OpenRouter API key** from https://openrouter.ai/
2. **Update .env** with your key
3. **Restart backend** to apply changes
4. **Update widget** to send transcript and play audio
5. **Test thoroughly** with different queries
6. **Monitor usage** on OpenRouter dashboard
7. **Deploy to production** when ready

---

## 📞 Support

**OpenRouter Documentation:** https://openrouter.ai/docs
**GPT-4o Audio Preview:** https://openrouter.ai/models/openai/gpt-4o-audio-preview

---

**Implementation Complete!** 🎉

Natural, human-like voice is now available for your voice agent platform.
