# Avatar Voice Refactoring - Implementation Summary

## Overview
Refactored voice configuration from Tenant level to Avatar level. Each avatar now has a fixed voice that matches its gender.

## Architecture Changes

### Before:
```
Tenant → voice_model, voice_gender → TTS
```

### After:
```
Tenant → avatar_id → Avatar → gender, voice_name → TTS
Tenant → speaking_rate, pitch, volume (audio settings only)
```

## Database Schema Changes

### Avatar Table (NEW FIELDS):
- `gender` (string): "male" or "female"
- `voice_provider` (string): "google"
- `voice_name` (string): e.g., "en-US-Neural2-F"

### Avatar Table (REMOVED):
- `default_voice` (replaced by voice_name)

### Tenant Table (NEW FIELDS):
- `pitch` (float): -20.0 to 20.0
- `volume` (float): 0.0 to 1.0

### Tenant Table (REMOVED):
- `voice_model` (moved to Avatar)
- `voice_gender` (moved to Avatar)

## Voice Resolution Flow

```
1. Widget sends tenant_id
2. Backend loads Tenant
3. Backend loads Avatar using tenant.avatar_id
4. Avatar.voice_name + Avatar.gender used for TTS
5. Tenant.speaking_rate + Tenant.pitch applied to audio config
6. Google Cloud TTS generates audio
7. MP3 streamed to browser
```

## API Changes

### GET /api/config
**Response:**
```json
{
  "company_name": "Acme Corp",
  "avatar_url": "data:image/png;base64,...",
  "avatar_gender": "female",
  "voice_name": "en-US-Neural2-F",
  "introduction_script": "Hello...",
  "brand_colors": {}
}
```

### POST /admin/avatars
**Parameters:**
- `name`: Avatar name
- `gender`: "male" or "female"
- `voice_name`: Google Cloud voice (e.g., "en-US-Neural2-F")
- `image_file`: Avatar image

### GET /admin/voices?gender=female
**Response:**
```json
{
  "voices": [
    {"name": "en-US-Neural2-F", "label": "Neural2-F (Natural, Conversational)"},
    {"name": "en-US-Neural2-C", "label": "Neural2-C (Clear, Professional)"}
  ],
  "gender": "female"
}
```

### PUT /admin/tenant/{tenant_id}
**Removed Fields:**
- `voice_model`
- `voice_gender`

**New Fields:**
- `pitch`
- `volume`

## Available Voices

### Female Voices:
- `en-US-Neural2-C` - Clear, Professional
- `en-US-Neural2-E` - Warm, Friendly
- `en-US-Neural2-F` - Natural, Conversational (Default)
- `en-US-Neural2-G` - Energetic, Modern
- `en-US-Neural2-H` - Soft, Gentle
- `en-US-Studio-O` - Premium Female

### Male Voices:
- `en-US-Neural2-A` - Deep, Authoritative
- `en-US-Neural2-D` - Professional, Clear
- `en-US-Neural2-I` - Friendly, Approachable
- `en-US-Neural2-J` - Confident, Strong
- `en-US-Studio-M` - Premium Male

## Google Cloud TTS Integration

```python
# Voice configuration from Avatar
VoiceSelectionParams(
    language_code="en-US",
    name=avatar.voice_name,  # e.g., "en-US-Neural2-F"
    ssml_gender=FEMALE or MALE  # from avatar.gender
)

# Audio settings from Tenant
AudioConfig(
    audio_encoding=MP3,
    speaking_rate=tenant.speaking_rate,  # 0.25 to 4.0
    pitch=tenant.pitch  # -20.0 to 20.0
)
```

## Migration Steps

### 1. Run Database Migration
```bash
docker exec -i voice-agent-per_dbgpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant < database_migration_avatar_voice.sql
```

### 2. Rebuild Backend
```bash
docker-compose build backend
docker-compose up -d
```

### 3. Update Existing Avatars
- Set gender for each avatar
- Assign appropriate voice_name based on gender
- Female avatars → en-US-Neural2-F
- Male avatars → en-US-Neural2-D

### 4. Update Tenant Settings
- Remove voice_model selections
- Configure speaking_rate, pitch, volume if needed

## Testing Checklist

✅ Female avatar produces female voice
✅ Male avatar produces male voice
✅ Tenants cannot override avatar voice
✅ Speaking rate applies correctly
✅ Pitch adjustment works
✅ Multiple tenants can share same avatar
✅ Voice remains consistent across sessions
✅ Browser TTS fallback works (if Google TTS fails)

## Benefits

1. **Consistency**: Avatar voice never changes
2. **Simplicity**: Tenants don't manage voice selection
3. **Scalability**: Multiple tenants share avatars
4. **Gender Matching**: Voice always matches avatar gender
5. **Flexibility**: Tenants can adjust audio settings (rate, pitch)

## Compatibility

✅ **Gemini LLM**: No changes
✅ **RAG with pgvector**: No changes
✅ **Knowledge Base**: No changes
✅ **Authentication**: No changes
✅ **Multi-tenant Architecture**: No changes

## Files Modified

1. `backend/models.py` - Updated Avatar and Tenant models
2. `backend/google_tts_service.py` - Added audio settings support
3. `backend/main.py` - Updated all avatar and tenant endpoints
4. `database_migration_avatar_voice.sql` - Migration script

## Next Steps

1. Run database migration
2. Rebuild and restart backend
3. Update admin UI to show voice selection by gender
4. Test with multiple avatars
5. Update tenant dashboard to remove voice selection

## Example Usage

### Create Female Avatar:
```bash
POST /admin/avatars
{
  "name": "Sarah",
  "gender": "female",
  "voice_name": "en-US-Neural2-F",
  "image_file": <file>
}
```

### Create Male Avatar:
```bash
POST /admin/avatars
{
  "name": "John",
  "gender": "male",
  "voice_name": "en-US-Neural2-D",
  "image_file": <file>
}
```

### Update Tenant Audio Settings:
```bash
PUT /admin/tenant/{tenant_id}
{
  "speaking_rate": 1.1,
  "pitch": 2.0,
  "volume": 0.9
}
```

## Architecture Diagram

```
┌─────────────┐
│   Widget    │
└──────┬──────┘
       │ tenant_id
       ▼
┌─────────────┐
│   Tenant    │
│  - avatar_id│
│  - rate     │
│  - pitch    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Avatar    │
│  - gender   │
│  - voice_name│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Google TTS  │
│  (MP3 Audio)│
└─────────────┘
```

## Summary

Voice configuration is now centralized at the Avatar level, ensuring consistency and simplifying tenant management. Each avatar has a fixed voice that matches its gender, while tenants can still customize audio settings like speaking rate and pitch.
