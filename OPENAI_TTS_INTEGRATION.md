# OpenAI TTS Integration - Implementation Summary

## Overview
Successfully integrated OpenAI Text-to-Speech API while keeping Google Gemini for LLM reasoning.

## Architecture Flow
```
Browser STT (Web Speech API)
  ↓
Backend receives transcript
  ↓
Gemini API (text generation with RAG)
  ↓
OpenAI TTS API (convert response to audio)
  ↓
Stream MP3 audio back to browser
  ↓
Browser plays audio
```

## Files Modified

### 1. `.env`
- Added `OPENAI_API_KEY`
- Added `OPENAI_TTS_MODEL=tts-1`
- Added `DEFAULT_VOICE=nova`

### 2. `backend/config.py`
- Added OpenAI configuration fields to Settings class

### 3. `backend/openai_tts_service.py` (NEW)
- Created OpenAITTSService class
- Implements `generate_audio(text, voice)` method
- Returns MP3 audio bytes
- Handles API errors gracefully

### 4. `backend/main.py`
- Updated `/api/introduction` endpoint to use OpenAI TTS
- Updated `/api/voice-query` endpoint to use OpenAI TTS
- Both endpoints return StreamingResponse with audio/mpeg
- Fallback to text response if TTS fails
- Added logging for voice model and generation time

### 5. `widget/voice-agent-widget.js`
- Removed speechSynthesis (browser TTS) usage
- Added audio blob handling
- Uses HTMLAudioElement for playback
- Handles both audio and text responses (fallback)
- Simplified code structure

## Voice Models Supported
- `nova` (female) - Default
- `alloy` (neutral female)
- `shimmer` (female)
- `echo` (male)
- `fable` (male)
- `onyx` (male)

## Multi-Tenant Support
- Each tenant has `voice_model` field in database
- Voice setting loaded per request
- No cross-tenant data sharing
- Tenant-specific voice in both introduction and responses

## Error Handling
- If OpenAI TTS fails, returns text response
- Widget falls back to browser TTS if needed
- Logs all errors for debugging
- Conversation continues even if TTS fails

## Logging
Each request logs:
- `tenant_id`
- `conversation_id` (session_id)
- `user_query` (transcript)
- `gemini_response` (text)
- `tts_voice_used`
- `audio_generation_time`

## Testing Checklist
1. ✅ Add OPENAI_API_KEY to .env
2. ✅ Restart backend: `docker-compose restart backend`
3. ✅ Test introduction audio plays
4. ✅ Test voice query returns audio
5. ✅ Test different voice models (nova, onyx, etc.)
6. ✅ Test fallback when API key is invalid
7. ✅ Verify same voice for introduction and responses
8. ✅ Check browser console for logs
9. ✅ Verify multi-tenant isolation

## API Endpoints

### GET /api/introduction
**Response**: audio/mpeg (MP3 stream)
**Headers**: X-Voice-Model

### POST /api/voice-query
**Request**: FormData with `transcript` and `session_id`
**Response**: audio/mpeg (MP3 stream)
**Headers**: X-Session-ID, X-Voice-Model

## Cost Estimation
OpenAI TTS Pricing: $15 per 1M characters
- Average response: 100 characters = $0.0015
- 1000 conversations = $1.50
- Very affordable for production use

## Next Steps
1. Add OPENAI_API_KEY to production .env
2. Deploy updated code
3. Test with real tenants
4. Monitor API usage and costs
5. Consider caching introduction audio per tenant
6. Add voice preview in admin dashboard

## Gemini Integration (Unchanged)
- Gemini handles all LLM reasoning
- RAG with pgvector for knowledge retrieval
- Multi-tenant knowledge base isolation
- Conversation history tracking
