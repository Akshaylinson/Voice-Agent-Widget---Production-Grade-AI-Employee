# 🚀 Quick Start - Test Voice Widget NOW

## 3 Simple Steps

### Step 1: Restart Backend (30 seconds)
```bash
# Double-click this file:
restart-backend.bat

# Or run manually:
docker-compose restart backend
```

### Step 2: Clear Browser Cache (10 seconds)
1. Press `Ctrl + Shift + Delete`
2. Check "Cached images and files"
3. Click "Clear data"

### Step 3: Test Widget (1 minute)
1. **Open demo page:**
   - Double-click `CodelessAi.html` OR
   - Double-click `demo_acme.html`

2. **Open console:**
   - Press `F12`
   - Click "Console" tab

3. **Activate widget:**
   - Click the floating avatar (bottom-right)
   - Allow microphone when prompted

4. **Listen for introduction:**
   - Should hear AI greeting
   - Console shows: `[WIDGET] Playing...`

5. **Speak your question:**
   - Say: "What services do you offer?"
   - Wait for response

## What You Should See

### ✅ Success Indicators:
- Avatar appears in bottom-right corner
- Introduction plays (voice or text-to-speech)
- Microphone icon turns red when listening
- Avatar pulses when speaking
- Console shows clear logs

### ❌ If Something's Wrong:

**No avatar appears:**
- Check: Is backend running? `docker-compose ps`
- Fix: Run `docker-compose up -d`

**No introduction plays:**
- Check: Console logs (F12)
- Expected: `[WIDGET] Playing browser TTS` (fallback working)

**"not-allowed" error:**
- Check: Microphone permissions
- Fix: Click lock icon in address bar → Allow microphone

**"no-speech" error:**
- Check: Is microphone working?
- Fix: Speak louder, reduce background noise

## Console Log Examples

### Working (Google Cloud TTS):
```
[WIDGET] Activating voice assistant
[WIDGET] Playing Google Cloud TTS audio
[WIDGET] Speech recognition started
```

### Working (Browser TTS Fallback):
```
[WIDGET] Activating voice assistant
[WIDGET] Playing browser TTS: Hello! I'm your...
[WIDGET] Browser TTS started
[WIDGET] Speech recognition started
```

### Error (Needs Fix):
```
[WIDGET] Speech recognition error: not-allowed
→ Fix: Allow microphone permissions
```

## Test Questions

Try asking:
- "What services do you offer?"
- "Tell me about your pricing"
- "How does your AI work?"
- "What is Codeless AI?"

## Access URLs

| Page | URL | Purpose |
|------|-----|---------|
| **Admin Dashboard** | http://localhost:3000 | Manage tenants |
| **CodelessAi Demo** | Open file directly | Test Codeless AI |
| **Acme Demo** | Open file directly | Test Acme Corp |
| **Backend API** | http://localhost:8000/health | Check status |

## Troubleshooting

### Backend not running?
```bash
docker-compose up -d
docker-compose ps
```

### Widget not loading?
1. Clear cache (Ctrl+Shift+Delete)
2. Hard reload (Ctrl+F5)
3. Check console for errors

### No audio?
- Browser TTS fallback should work automatically
- Check console: Should see `[WIDGET] Playing browser TTS`
- If not, check browser audio settings

## Need More Help?

📖 **Detailed Guides:**
- `ACCESS_GUIDE.md` - How to access each page
- `WIDGET_TROUBLESHOOTING.md` - Detailed troubleshooting
- `FIXES_APPLIED.md` - What was fixed and why

🔍 **Check Logs:**
```bash
# Backend logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend
```

## Success Criteria

✅ You're successful when:
1. Avatar appears on page
2. Introduction plays (any TTS method)
3. Can speak and get transcribed
4. AI responds with voice
5. Can have continuous conversation

---

**Ready?** Run `restart-backend.bat` and test! 🎉
