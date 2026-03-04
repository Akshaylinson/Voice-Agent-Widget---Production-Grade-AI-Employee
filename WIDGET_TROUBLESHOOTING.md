# 🔧 Voice Widget Troubleshooting Guide

## Issue: No Introduction Audio Playing

### Root Causes:
1. **Google Cloud TTS not configured** - Missing API credentials
2. **Audio playback blocked** - Browser autoplay policy
3. **Network/CORS issues** - API not accessible

### Solution Implemented:
✅ **Automatic Fallback System**
- Widget now tries Google Cloud TTS first
- If fails, automatically falls back to Browser TTS
- No manual intervention needed

---

## How It Works Now

### Audio Flow:
```
1. User clicks avatar
2. Widget requests introduction from backend
3. Backend tries Google Cloud TTS
   ├─ Success → Returns MP3 audio
   └─ Failure → Returns JSON with text
4. Widget receives response
   ├─ Audio → Plays MP3
   └─ Text → Uses browser TTS
5. After intro, starts listening
```

### Voice Query Flow:
```
1. User speaks
2. Browser STT transcribes
3. Backend processes with Gemini LLM
4. Backend tries Google Cloud TTS
   ├─ Success → Returns MP3 audio
   └─ Failure → Returns JSON with text
5. Widget plays response
   ├─ Audio → Plays MP3
   └─ Text → Uses browser TTS
6. Returns to listening
```

---

## Testing the Fix

### 1. Restart Backend
```bash
cd "e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)"
docker-compose restart backend
```

### 2. Clear Browser Cache
- Press `Ctrl + Shift + Delete`
- Clear cached files
- Reload page

### 3. Test Widget
1. Open `CodelessAi.html` or `demo_acme.html`
2. Click avatar
3. Check console (F12) for logs:
   - `[WIDGET] Playing Google Cloud TTS audio` ✅ Google TTS working
   - `[WIDGET] Playing browser TTS` ✅ Fallback working

---

## Console Log Guide

### Good Logs (Working):
```
[WIDGET] Initializing Voice Agent Widget
[WIDGET] Config loaded
[WIDGET] Activating voice assistant
[WIDGET] Playing Google Cloud TTS audio  ← Audio playing
[WIDGET] Speech recognition started
```

### Fallback Logs (Also Working):
```
[WIDGET] Initializing Voice Agent Widget
[WIDGET] Config loaded
[WIDGET] Activating voice assistant
[WIDGET] No audio, trying browser TTS fallback
[WIDGET] Playing browser TTS  ← Browser TTS working
[WIDGET] Browser TTS started
[WIDGET] Speech recognition started
```

### Error Logs (Needs Fix):
```
[WIDGET] Speech recognition error: not-allowed
```
**Fix:** Allow microphone permissions in browser

```
[WIDGET] Speech recognition error: no-speech
```
**Fix:** Speak louder or check microphone

---

## Google Cloud TTS Setup (Optional)

If you want to use Google Cloud TTS instead of browser TTS:

### 1. Get Google Cloud Credentials
1. Go to https://console.cloud.google.com
2. Create project
3. Enable "Cloud Text-to-Speech API"
4. Create service account
5. Download JSON key

### 2. Configure Backend
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Or add to docker-compose.yml
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
volumes:
  - ./google-credentials.json:/app/google-credentials.json
```

### 3. Restart
```bash
docker-compose restart backend
```

---

## Browser TTS Voice Selection

The widget automatically selects voices based on avatar gender:
- **Female avatars** → Female browser voices
- **Male avatars** → Male browser voices

### Available Browser Voices:
Check in console:
```javascript
speechSynthesis.getVoices().forEach(v => console.log(v.name, v.lang))
```

Common voices:
- `Microsoft Zira - English (United States)` (Female)
- `Microsoft David - English (United States)` (Male)
- `Google US English` (Female)
- `Google UK English Male`

---

## Common Issues

### Issue: "no-speech" Error
**Cause:** Microphone not detecting speech
**Fix:**
- Speak louder
- Check microphone is working
- Reduce background noise
- Try different browser (Chrome recommended)

### Issue: Introduction Plays But No Listening
**Cause:** Speech recognition not starting
**Fix:**
- Check browser console for errors
- Ensure HTTPS (required for mic access in production)
- Try Chrome/Edge (best support)

### Issue: Widget Not Appearing
**Cause:** JavaScript not loading
**Fix:**
- Check network tab (F12)
- Verify API URL is correct
- Check CORS settings

---

## Production Checklist

Before deploying to production:

- [ ] Use HTTPS (required for microphone)
- [ ] Configure Google Cloud TTS (better quality)
- [ ] Set up proper CORS origins
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Monitor backend logs
- [ ] Set up error tracking

---

## Support

If issues persist:
1. Check backend logs: `docker-compose logs backend`
2. Check browser console (F12)
3. Verify tenant configuration in admin dashboard
4. Ensure avatar is assigned to tenant
5. Test with different browser

---

**Last Updated:** 2024
**Version:** 3.0 (Gemini + Google TTS + Browser TTS Fallback)
