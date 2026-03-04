# Google Cloud TTS - Quick Setup Guide

## ✅ Installation Complete

Your Voice Agent is now running with Google Cloud Text-to-Speech integration!

## 🔧 Next Steps to Enable TTS

### 1. Create Google Cloud Project

```bash
# Go to https://console.cloud.google.com/
# Create a new project or select existing one
```

### 2. Enable Text-to-Speech API

```bash
# In Google Cloud Console:
# 1. Go to "APIs & Services" > "Library"
# 2. Search for "Cloud Text-to-Speech API"
# 3. Click "Enable"
```

### 3. Create Service Account

```bash
# In Google Cloud Console:
# 1. Go to "IAM & Admin" > "Service Accounts"
# 2. Click "Create Service Account"
# 3. Name: voice-agent-tts
# 4. Grant role: "Cloud Text-to-Speech User"
# 5. Click "Done"
```

### 4. Download Service Account Key

```bash
# 1. Click on the service account you just created
# 2. Go to "Keys" tab
# 3. Click "Add Key" > "Create new key"
# 4. Choose JSON format
# 5. Save the file as service-account.json
```

### 5. Update .env File

Edit `e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)\.env`:

```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
DEFAULT_VOICE=en-US-Neural2-F
```

### 6. Copy Service Account Key to Backend

```bash
# Copy the service-account.json to backend directory
copy service-account.json "e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)\backend\service-account.json"
```

### 7. Restart Backend Container

```bash
cd "e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)"
docker-compose restart backend
```

## 🎤 Available Voices

### Female Voices
- `en-US-Neural2-C` - Clear, professional
- `en-US-Neural2-E` - Warm, friendly
- `en-US-Neural2-F` - Natural, conversational (Default)
- `en-US-Neural2-G` - Energetic, modern
- `en-US-Neural2-H` - Soft, gentle

### Male Voices
- `en-US-Neural2-A` - Deep, authoritative
- `en-US-Neural2-D` - Professional, clear
- `en-US-Neural2-I` - Friendly, approachable
- `en-US-Neural2-J` - Confident, strong

## 🧪 Testing

### 1. Check Backend Logs
```bash
docker logs voice-agent-per_dbgpt-auido-mini-backend-1
```

### 2. Test Introduction Audio
Open: http://localhost:3000 (Admin Dashboard)
- Create a tenant
- Set introduction script
- Select voice model
- Test the widget

### 3. Test Voice Query
- Click the avatar in the widget
- Speak a question
- Listen for the response

## 🔍 Troubleshooting

### Error: "GOOGLE_APPLICATION_CREDENTIALS not found"
**Solution**: Make sure service-account.json is in the backend directory and .env has correct path

### Error: "Permission denied"
**Solution**: Ensure service account has "Cloud Text-to-Speech User" role

### Error: "API not enabled"
**Solution**: Enable Cloud Text-to-Speech API in Google Cloud Console

### No audio playing
**Solution**: 
1. Check browser console for errors
2. Verify CORS settings
3. Check backend logs: `docker logs voice-agent-per_dbgpt-auido-mini-backend-1`

## 💰 Pricing

Google Cloud TTS Pricing:
- Neural2 voices: $16 per 1 million characters
- First 1 million characters per month: FREE
- Average conversation (100 chars): $0.0016
- 1000 conversations: ~$1.60

Very affordable for production use!

## 📊 Current Status

✅ Backend running with Google Cloud TTS support
✅ Widget updated to play audio streams
✅ Multi-tenant voice configuration ready
⏳ Waiting for Google Cloud credentials

## 🚀 Once Credentials Are Added

Your voice agent will:
- Use high-quality Neural2 voices
- Have consistent voice across all devices
- Support multiple voice models per tenant
- Provide professional audio quality

## 📝 Alternative: Use Browser TTS (Temporary)

If you want to test without Google Cloud setup:
- The system will automatically fallback to browser TTS
- Voice quality will vary by browser/device
- No API costs
- Good for development/testing

## 🔗 Useful Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Voice List](https://cloud.google.com/text-to-speech/docs/voices)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

## ✅ Summary

Your system is ready! Just add Google Cloud credentials to enable high-quality TTS.

**Current Architecture:**
```
Browser STT → Gemini LLM (with RAG) → Google Cloud TTS → Browser Audio
```

**Services Running:**
- Database: http://localhost:5432
- Backend API: http://localhost:8000
- Admin Dashboard: http://localhost:3000
