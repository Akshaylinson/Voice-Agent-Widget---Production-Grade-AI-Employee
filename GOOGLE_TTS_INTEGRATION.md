# Google Cloud Text-to-Speech Integration

## Overview
Replaced OpenAI TTS with Google Cloud Text-to-Speech while keeping Gemini for LLM reasoning.

## Architecture Flow
```
Browser STT (Web Speech API)
  ↓
Backend receives transcript
  ↓
Gemini API (text generation with RAG + pgvector)
  ↓
Google Cloud TTS (convert response to audio)
  ↓
Stream MP3 audio back to browser
  ↓
Browser plays audio
```

## Files Modified

### 1. `.env`
- Added `GOOGLE_CLOUD_PROJECT_ID`
- Added `GOOGLE_APPLICATION_CREDENTIALS`
- Added `DEFAULT_VOICE=en-US-Neural2-F`
- Removed OpenAI configuration

### 2. `backend/requirements.txt`
- Added `google-cloud-texttospeech==2.14.1`

### 3. `backend/config.py`
- Replaced OpenAI TTS config with Google Cloud TTS config

### 4. `backend/google_tts_service.py` (NEW)
- Created GoogleTTSService class
- Implements `generate_audio(text, voice)` method
- Returns MP3 audio bytes
- Maps OpenAI-style voice names to Google voices
- Handles API errors gracefully

### 5. `backend/main.py`
- Updated `/api/introduction` endpoint to use Google Cloud TTS
- Updated `/api/voice-query` endpoint to use Google Cloud TTS
- Both endpoints return StreamingResponse with audio/mpeg
- Fallback to text response if TTS fails
- Added logging for voice model and generation time

### 6. `backend/openai_tts_service.py` (REMOVED)
- Deleted old OpenAI TTS service

### 7. `widget/voice-agent-widget.js` (NO CHANGES)
- Already handles audio blob playback
- Works with any server-side TTS

## Voice Configuration

### Google Cloud Neural2 Voices
- `en-US-Neural2-A` (Male)
- `en-US-Neural2-C` (Female)
- `en-US-Neural2-D` (Male)
- `en-US-Neural2-E` (Female)
- `en-US-Neural2-F` (Female) - Default
- `en-US-Neural2-G` (Female)
- `en-US-Neural2-H` (Female)
- `en-US-Neural2-I` (Male)
- `en-US-Neural2-J` (Male)

### Voice Mapping (OpenAI-style to Google)
```python
"nova" → "en-US-Neural2-F" (Female)
"shimmer" → "en-US-Neural2-C" (Female)
"alloy" → "en-US-Neural2-E" (Female)
"onyx" → "en-US-Neural2-D" (Male)
"fable" → "en-US-Neural2-A" (Male)
"echo" → "en-US-Neural2-J" (Male)
```

## Setup Instructions

### 1. Create Google Cloud Project
```bash
# Create project
gcloud projects create your-project-id

# Enable Text-to-Speech API
gcloud services enable texttospeech.googleapis.com
```

### 2. Create Service Account
```bash
# Create service account
gcloud iam service-accounts create voice-agent-tts \
    --display-name="Voice Agent TTS"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:voice-agent-tts@your-project-id.iam.gserviceaccount.com" \
    --role="roles/cloudtexttospeech.user"

# Create key
gcloud iam service-accounts keys create service-account.json \
    --iam-account=voice-agent-tts@your-project-id.iam.gserviceaccount.com
```

### 3. Update .env
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
DEFAULT_VOICE=en-US-Neural2-F
```

### 4. Deploy
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Restart backend
docker-compose restart backend
```

## Multi-Tenant Support
- Each tenant has `voice_model` field in database
- Voice setting loaded per request
- No cross-tenant data sharing
- Tenant-specific voice in both introduction and responses

## Error Handling
- If Google Cloud TTS fails, returns text response
- Widget falls back to browser TTS if needed
- Logs all errors for debugging
- Conversation continues even if TTS fails

## Security
- Service account credentials stored server-side only
- Never exposed to frontend
- All TTS calls run in backend
- Credentials file path in environment variable

## Logging
Each request logs:
- `tenant_id`
- `session_id`
- `user_query` (transcript)
- `gemini_response` (text)
- `tts_voice_used`
- `audio_generation_time`

## Cost Estimation
Google Cloud TTS Pricing:
- Neural2 voices: $16 per 1M characters
- Average response: 100 characters = $0.0016
- 1000 conversations = $1.60
- Very affordable for production use

## Testing Checklist
1. ✅ Create Google Cloud project
2. ✅ Enable Text-to-Speech API
3. ✅ Create service account and download key
4. ✅ Update .env with credentials
5. ✅ Install dependencies: `pip install -r requirements.txt`
6. ✅ Restart backend: `docker-compose restart backend`
7. ✅ Test introduction audio plays
8. ✅ Test voice query returns audio
9. ✅ Test different voice models
10. ✅ Test fallback when credentials are invalid
11. ✅ Verify same voice for introduction and responses
12. ✅ Check browser console for logs
13. ✅ Verify multi-tenant isolation

## API Endpoints

### GET /api/introduction
**Response**: audio/mpeg (MP3 stream)
**Headers**: X-Voice-Model

### POST /api/voice-query
**Request**: FormData with `transcript` and `session_id`
**Response**: audio/mpeg (MP3 stream)
**Headers**: X-Session-ID, X-Voice-Model

## Advantages Over OpenAI TTS
1. **Same Ecosystem**: Uses Google Cloud like Gemini
2. **More Voices**: 40+ Neural2 voices available
3. **Better Integration**: Single cloud provider
4. **SSML Support**: Advanced speech markup
5. **Custom Voices**: Can train custom voices
6. **Lower Latency**: Optimized for Google infrastructure

## Gemini Integration (Unchanged)
- Gemini handles all LLM reasoning
- RAG with pgvector for knowledge retrieval
- Multi-tenant knowledge base isolation
- Conversation history tracking
- Embedding generation for semantic search

## Next Steps
1. Set up Google Cloud project and credentials
2. Deploy updated code
3. Test with real tenants
4. Monitor API usage and costs
5. Consider caching introduction audio per tenant
6. Add voice preview in admin dashboard
7. Explore SSML for advanced speech control
