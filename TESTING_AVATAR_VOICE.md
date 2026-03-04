# Avatar Voice Refactoring - Testing Guide

## ✅ Implementation Complete

The voice configuration has been successfully moved from Tenant to Avatar level!

## 🧪 Testing Steps

### 1. Test Voice List Endpoint

```bash
# Get all voices
curl http://localhost:8000/admin/voices

# Get female voices only
curl http://localhost:8000/admin/voices?gender=female

# Get male voices only
curl http://localhost:8000/admin/voices?gender=male
```

### 2. Create Female Avatar

```bash
curl -X POST http://localhost:8000/admin/avatars \
  -F "name=Sarah" \
  -F "gender=female" \
  -F "voice_name=en-US-Neural2-F" \
  -F "image_file=@avatar_female.png"
```

Expected Response:
```json
{
  "id": "uuid-here",
  "name": "Sarah",
  "gender": "female",
  "voice_name": "en-US-Neural2-F"
}
```

### 3. Create Male Avatar

```bash
curl -X POST http://localhost:8000/admin/avatars \
  -F "name=John" \
  -F "gender=male" \
  -F "voice_name=en-US-Neural2-D" \
  -F "image_file=@avatar_male.png"
```

Expected Response:
```json
{
  "id": "uuid-here",
  "name": "John",
  "gender": "male",
  "voice_name": "en-US-Neural2-D"
}
```

### 4. List All Avatars

```bash
curl http://localhost:8000/admin/avatars
```

Expected Response:
```json
[
  {
    "id": "uuid-1",
    "name": "Sarah",
    "gender": "female",
    "voice_name": "en-US-Neural2-F",
    "voice_provider": "google",
    "image_data": "data:image/png;base64,..."
  },
  {
    "id": "uuid-2",
    "name": "John",
    "gender": "male",
    "voice_name": "en-US-Neural2-D",
    "voice_provider": "google",
    "image_data": "data:image/png;base64,..."
  }
]
```

### 5. Update Tenant with Avatar

```bash
curl -X PUT http://localhost:8000/admin/tenant/{tenant_id} \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "uuid-of-sarah-avatar",
    "speaking_rate": 1.1,
    "pitch": 2.0
  }'
```

### 6. Test Widget Configuration

```bash
curl http://localhost:8000/api/config \
  -H "X-Tenant-ID: your-tenant-id" \
  -H "X-Signature: your-signature"
```

Expected Response:
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

### 7. Test Introduction Audio

```bash
curl http://localhost:8000/api/introduction \
  -H "X-Tenant-ID: your-tenant-id" \
  -H "X-Signature: your-signature" \
  --output introduction.mp3
```

Play the audio file and verify:
- ✅ Female avatar produces female voice
- ✅ Male avatar produces male voice
- ✅ Voice matches avatar gender

### 8. Test Voice Query

```bash
curl -X POST http://localhost:8000/api/voice-query \
  -H "X-Tenant-ID: your-tenant-id" \
  -H "X-Signature: your-signature" \
  -F "transcript=What services do you offer?" \
  --output response.mp3
```

Play the audio file and verify:
- ✅ Voice matches avatar configuration
- ✅ Speaking rate applied correctly
- ✅ Pitch adjustment works

## 🎯 Verification Checklist

### Database Schema
- ✅ `avatars.gender` column exists
- ✅ `avatars.voice_provider` column exists
- ✅ `avatars.voice_name` column exists
- ✅ `avatars.default_voice` column removed
- ✅ `tenants.pitch` column exists
- ✅ `tenants.volume` column exists
- ✅ `tenants.voice_model` column removed
- ✅ `tenants.voice_gender` column removed

### API Endpoints
- ✅ `GET /admin/voices` returns voice list
- ✅ `GET /admin/voices?gender=female` filters by gender
- ✅ `POST /admin/avatars` accepts gender and voice_name
- ✅ `GET /admin/avatars` returns voice configuration
- ✅ `PUT /admin/avatar/{id}` updates voice settings
- ✅ `GET /api/config` returns avatar_gender and voice_name
- ✅ `GET /api/introduction` uses avatar voice
- ✅ `POST /api/voice-query` uses avatar voice

### Voice Behavior
- ✅ Female avatar always produces female voice
- ✅ Male avatar always produces male voice
- ✅ Tenants cannot override avatar voice
- ✅ Speaking rate applies correctly
- ✅ Pitch adjustment works
- ✅ Multiple tenants can share same avatar
- ✅ Voice remains consistent across sessions

### Compatibility
- ✅ Gemini LLM works unchanged
- ✅ RAG with pgvector works unchanged
- ✅ Knowledge base works unchanged
- ✅ Authentication works unchanged
- ✅ Multi-tenant architecture works unchanged

## 🐛 Troubleshooting

### Error: "Column 'gender' does not exist"
**Solution**: Run database migration
```bash
docker exec -i voice-agent-per_dbgpt-auido-mini-db-1 psql -U postgres -d voice_agent_multi_tenant < database_migration_avatar_voice.sql
```

### Error: "No avatar found"
**Solution**: Ensure tenant has valid avatar_id assigned

### Wrong voice gender
**Solution**: 
1. Check avatar.gender in database
2. Verify avatar.voice_name matches gender
3. Update avatar if needed

### Voice settings not applying
**Solution**:
1. Check tenant.speaking_rate and tenant.pitch values
2. Ensure values are within valid ranges
3. Restart backend: `docker-compose restart backend`

## 📊 Database Queries

### Check Avatar Configuration
```sql
SELECT id, name, gender, voice_name, voice_provider 
FROM avatars;
```

### Check Tenant Audio Settings
```sql
SELECT id, company_name, avatar_id, speaking_rate, pitch, volume 
FROM tenants;
```

### Verify Migration
```sql
-- Should return 0 rows (columns removed)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'tenants' 
AND column_name IN ('voice_model', 'voice_gender');

-- Should return 3 rows (columns added)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'avatars' 
AND column_name IN ('gender', 'voice_provider', 'voice_name');
```

## 🎉 Success Criteria

Your refactoring is successful if:

1. ✅ Avatars have gender and voice_name fields
2. ✅ Tenants no longer have voice_model field
3. ✅ Female avatars produce female voices
4. ✅ Male avatars produce male voices
5. ✅ Tenants can adjust speaking_rate and pitch
6. ✅ Voice remains consistent for each avatar
7. ✅ Multiple tenants can share avatars
8. ✅ All existing functionality still works

## 📝 Next Steps

1. Update admin UI to show voice selection by gender
2. Add voice preview feature
3. Test with multiple tenants and avatars
4. Update tenant dashboard to remove voice selection
5. Add voice customization options (if needed)

## 🔗 Related Documentation

- `AVATAR_VOICE_REFACTORING.md` - Implementation details
- `GOOGLE_TTS_INTEGRATION.md` - TTS setup guide
- `database_migration_avatar_voice.sql` - Migration script
