# Admin Dashboard - Avatar Voice Configuration Guide

## ✅ CORS Issue Fixed

The admin dashboard now works correctly with the backend API.

## 🎯 New Features

### 1. Avatar Creation with Voice Configuration

When creating a new avatar, you must now specify:
- **Avatar Name**: Display name
- **Gender**: Male or Female
- **Voice Model**: Automatically filtered by gender
- **Image**: Avatar picture

### 2. Voice Selection by Gender

**Female Voices:**
- Neural2-C (Clear, Professional)
- Neural2-E (Warm, Friendly)
- Neural2-F (Natural, Conversational) - Default
- Neural2-G (Energetic, Modern)
- Neural2-H (Soft, Gentle)
- Studio-O (Premium Female)

**Male Voices:**
- Neural2-A (Deep, Authoritative)
- Neural2-D (Professional, Clear)
- Neural2-I (Friendly, Approachable)
- Neural2-J (Confident, Strong)
- Studio-M (Premium Male)

### 3. Tenant Creation Simplified

When creating a tenant:
- Select an avatar (voice comes from avatar)
- No voice model selection needed
- Avatar determines the voice automatically

## 📊 How to Use

### Step 1: Create Avatars

1. Go to **Avatar Gallery** section
2. Click **+ Add Avatar**
3. Fill in:
   - Name: e.g., "Sarah"
   - Gender: Female
   - Voice Model: Select from filtered list
   - Upload image
4. Click **Create**

### Step 2: Create Tenants

1. Go to **Tenants** section
2. Fill in:
   - Company Name
   - Domain
   - Select Avatar (voice is inherited)
   - Introduction Script
3. Click **Create Tenant**

### Step 3: Test

1. Open the widget on your website
2. Click the avatar
3. Listen to the introduction
4. Verify the voice matches the avatar gender

## 🔧 Troubleshooting

### CORS Error
**Fixed!** The dashboard now properly communicates with the backend.

### "Failed to load tenants"
**Solution**: Ensure backend is running on port 8000
```bash
docker ps | grep backend
```

### "Failed to load voices"
**Solution**: Check backend logs
```bash
docker logs voice-agent-per_dbgpt-auido-mini-backend-1
```

### Avatar not showing voice
**Solution**: Ensure avatar has gender and voice_name set in database

## 🎨 UI Changes

### Removed:
- Voice model selection from tenant creation
- Voice gender selection from tenant creation

### Added:
- Gender selection in avatar creation
- Voice model selection (filtered by gender) in avatar creation
- Avatar voice preview in tenant creation

## 📝 API Endpoints Used

- `GET /admin/tenants` - List all tenants
- `POST /admin/tenants` - Create tenant
- `GET /admin/avatars` - List all avatars
- `POST /admin/avatars` - Create avatar with voice
- `GET /admin/voices?gender=female` - Get voices by gender

## ✅ Success Indicators

You'll know it's working when:
1. ✅ Admin dashboard loads without CORS errors
2. ✅ Avatars show gender and voice name
3. ✅ Voice selection is filtered by gender
4. ✅ Tenants show avatar information
5. ✅ Widget uses avatar voice automatically

## 🚀 Next Steps

1. Create multiple avatars (male and female)
2. Assign avatars to tenants
3. Test voice consistency
4. Update tenant dashboard (if needed)

## 📖 Related Documentation

- `AVATAR_VOICE_REFACTORING.md` - Technical details
- `TESTING_AVATAR_VOICE.md` - Testing guide
- `GOOGLE_TTS_INTEGRATION.md` - TTS setup

## 🎉 Benefits

- **Simplified**: Tenants don't manage voices
- **Consistent**: Avatar voice never changes
- **Professional**: Gender-matched voices
- **Scalable**: Multiple tenants share avatars
