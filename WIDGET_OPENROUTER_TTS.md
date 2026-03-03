# Widget Integration Guide - OpenRouter TTS

## Architecture Flow

```
Browser (User speaks)
    ↓
Web Speech API (STT) → Transcript text
    ↓
POST /api/voice-query {transcript: "..."}
    ↓
Backend:
  1. OpenRouter GPT-4o-mini → Response text
  2. OpenRouter GPT-4o Audio Preview → Audio bytes
    ↓
StreamingResponse (audio/mpeg)
    ↓
Browser plays audio
```

---

## Widget Changes Required

### Current Widget (widget.js)

The widget needs to:
1. Use Web Speech API for STT (already does this)
2. Send **transcript text** instead of audio file
3. Receive **audio blob** response
4. Play audio directly

### Updated Voice Query Function

```javascript
async function sendVoiceQuery(transcript, sessionId) {
    try {
        console.log('[WIDGET] Sending transcript:', transcript);
        
        // Send transcript as form data
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
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        // Get audio blob
        const audioBlob = await response.blob();
        console.log('[WIDGET] Received audio:', audioBlob.size, 'bytes');
        
        // Play audio
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            console.log('[WIDGET] Audio playback finished');
        };
        
        await audio.play();
        
    } catch (error) {
        console.error('[WIDGET] Voice query error:', error);
        throw error;
    }
}
```

### Updated Introduction Function

```javascript
async function playIntroduction() {
    try {
        console.log('[WIDGET] Fetching introduction audio');
        
        const response = await fetch(`${API_URL}/introduction`, {
            headers: {
                'X-Tenant-ID': TENANT_ID,
                'X-Signature': SIGNATURE
            }
        });
        
        if (!response.ok) {
            console.error('[WIDGET] Introduction fetch failed');
            return;
        }
        
        const audioBlob = await response.blob();
        
        if (audioBlob.size === 0) {
            console.log('[WIDGET] No introduction audio');
            return;
        }
        
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            console.log('[WIDGET] Introduction finished');
            startListening(); // Start listening after intro
        };
        
        await audio.play();
        
    } catch (error) {
        console.error('[WIDGET] Introduction error:', error);
        startListening(); // Start anyway
    }
}
```

### Complete Widget Flow

```javascript
// 1. User clicks avatar
avatarButton.addEventListener('click', async () => {
    await playIntroduction();
});

// 2. After introduction, start listening
function startListening() {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    
    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('[WIDGET] Heard:', transcript);
        
        // Send to backend
        await sendVoiceQuery(transcript, sessionId);
    };
    
    recognition.start();
}

// 3. Backend processes and returns audio
// 4. Widget plays audio
// 5. Loop back to listening
```

---

## Testing

### Test Introduction

```bash
curl -H "X-Tenant-ID: your-tenant-id" \
     -H "X-Signature: your-signature" \
     http://localhost:8000/api/introduction \
     --output intro.mp3

# Play the file
```

### Test Voice Query

```bash
curl -X POST \
  -H "X-Tenant-ID: your-tenant-id" \
  -H "X-Signature: your-signature" \
  -F "transcript=What services do you offer?" \
  -F "session_id=test-123" \
  http://localhost:8000/api/voice-query \
  --output response.mp3

# Play the file
```

---

## Error Handling

### Widget Side

```javascript
try {
    await sendVoiceQuery(transcript, sessionId);
} catch (error) {
    console.error('[WIDGET] Error:', error);
    
    // Show error to user
    showError('Sorry, I couldn\'t process that. Please try again.');
    
    // Restart listening
    setTimeout(() => startListening(), 2000);
}
```

### Backend Side

If OpenRouter TTS fails:
- Log error
- Return empty audio (widget handles gracefully)
- Or return error JSON (widget shows message)

---

## Environment Setup

### .env File

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_TTS_MODEL=openai/gpt-4o-audio-preview
OPENROUTER_HTTP_REFERER=http://localhost:8000
OPENROUTER_APP_TITLE=Codeless AI Voice Platform
```

### Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up / Login
3. Go to Keys section
4. Create new key
5. Copy to .env

---

## Voice Options

OpenRouter GPT-4o Audio Preview supports these voices:
- `alloy` - Neutral, balanced
- `echo` - Clear, professional
- `fable` - Warm, friendly
- `onyx` - Deep, authoritative
- `nova` - Energetic, modern
- `shimmer` - Soft, gentle

Set in tenant configuration via admin dashboard.

---

## Cost Estimation

### OpenRouter Pricing

**GPT-4o-mini (Text):**
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**GPT-4o Audio Preview (TTS):**
- Text input: $2.50 / 1M tokens
- Audio output: $100 / 1M tokens

**Example:**
- 100 conversations
- Average 50 words per response
- ~75 tokens per response
- Cost: ~$0.75 for text + ~$7.50 for audio = **$8.25 per 100 conversations**

---

## Advantages Over Browser TTS

| Feature | Browser TTS | OpenRouter TTS |
|---------|-------------|----------------|
| Voice Quality | ⭐⭐ Robotic | ⭐⭐⭐⭐⭐ Natural |
| Consistency | Varies by browser | Consistent |
| Customization | Limited | Full control |
| Offline | ✅ Works | ❌ Needs internet |
| Cost | Free | ~$0.08 per conversation |

---

## Deployment Checklist

- [ ] Update .env with OpenRouter API key
- [ ] Update backend code (openai_service.py, main.py)
- [ ] Update widget.js to send transcript
- [ ] Update widget.js to play audio blob
- [ ] Test introduction audio
- [ ] Test voice query flow
- [ ] Monitor OpenRouter usage
- [ ] Set up error handling
- [ ] Test on multiple browsers
- [ ] Deploy to production

---

## Troubleshooting

### No audio returned

**Check:**
1. OpenRouter API key is valid
2. Model name is correct: `openai/gpt-4o-audio-preview`
3. Backend logs show TTS call
4. Response has audio data

### Audio doesn't play

**Check:**
1. Browser console for errors
2. Audio blob size > 0
3. Content-Type is audio/mpeg
4. Browser supports audio playback

### Poor voice quality

**Try:**
1. Different voice model
2. Adjust text formatting
3. Add punctuation for better pacing
4. Use shorter sentences

---

**Ready to deploy!** 🚀
