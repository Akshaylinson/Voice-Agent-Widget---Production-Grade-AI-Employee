# Testing Avatar Voice Configuration - Step by Step

## The voice configuration fields ARE in the admin dashboard!

Follow these exact steps:

### Step 1: Clear Browser Cache
```
Press: Ctrl + Shift + Delete
Or: Ctrl + F5 (hard refresh)
```

### Step 2: Open Admin Dashboard
```
http://localhost:3000
```

### Step 3: Go to Avatar Gallery
1. Click "🎭 Avatar Gallery" in the left sidebar
2. You should see the Avatar Gallery page

### Step 4: Click "+ Add Avatar" Button
1. Look for the blue button in the top right: "+ Add Avatar"
2. Click it
3. A form should appear with these fields:

```
✅ Avatar Name (text input)
✅ Gender (dropdown: Female/Male)
✅ Voice Model (dropdown: filtered by gender)
✅ Upload Image (file input)
✅ Image Preview (shows after selecting file)
✅ Create button
✅ Cancel button
```

### Step 5: Fill the Form

**Example for Female Avatar:**
```
Avatar Name: Sarah
Gender: Female
Voice Model: Neural2-F (Natural, Conversational)
Upload Image: [select a PNG/JPG file]
```

**Example for Male Avatar:**
```
Avatar Name: John
Gender: Male
Voice Model: Neural2-D (Professional, Clear)
Upload Image: [select a PNG/JPG file]
```

### Step 6: Verify Voice Dropdown Changes
1. Select "Female" in Gender dropdown
2. Voice Model dropdown should show ONLY female voices:
   - Neural2-C (Clear, Professional)
   - Neural2-E (Warm, Friendly)
   - Neural2-F (Natural, Conversational)
   - Neural2-G (Energetic, Modern)
   - Neural2-H (Soft, Gentle)
   - Studio-O (Premium Female)

3. Change to "Male" in Gender dropdown
4. Voice Model dropdown should show ONLY male voices:
   - Neural2-A (Deep, Authoritative)
   - Neural2-D (Professional, Clear)
   - Neural2-I (Friendly, Approachable)
   - Neural2-J (Confident, Strong)
   - Studio-M (Premium Male)

### Step 7: Create Avatar
1. Fill all fields
2. Click "Create" button
3. You should see:
   - Success toast message
   - Form closes
   - New avatar appears in gallery
   - Avatar shows: Name, Gender, Voice Name

### Troubleshooting

#### Problem: Form doesn't appear when clicking "+ Add Avatar"
**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Hard refresh: Ctrl + Shift + R
4. Try different browser

#### Problem: Voice dropdown shows "Loading voices..."
**Solution:**
1. Check backend is running:
   ```bash
   docker ps | grep backend
   ```
2. Check backend logs:
   ```bash
   docker logs voice-agent-per_dbgpt-auido-mini-backend-1
   ```
3. Test API endpoint:
   ```
   http://localhost:8000/admin/voices
   ```

#### Problem: Can't see gender or voice fields
**Solution:**
1. Clear browser cache completely
2. Restart admin container:
   ```bash
   docker-compose restart admin
   ```
3. Hard refresh browser: Ctrl + F5

### Verify the HTML Contains Voice Fields

Check the source code in browser:
1. Right-click on page → "View Page Source"
2. Search for: `avatar_gender`
3. You should find:
```html
<select id="avatar_gender" onchange="loadVoicesByGender()">
    <option value="female">Female</option>
    <option value="male">Male</option>
</select>
```

4. Search for: `avatar_voice`
5. You should find:
```html
<select id="avatar_voice" class="w-full bg-slate-900...">
    <option value="">Loading voices...</option>
</select>
```

### Expected Result

After creating an avatar, you should see in the gallery:

```
┌─────────────────────┐
│   [Avatar Image]    │
│                     │
│       Sarah         │
│  female - en-US-    │
│    Neural2-F        │
└─────────────────────┘
```

### Test Complete Flow

1. ✅ Create female avatar with female voice
2. ✅ Create male avatar with male voice
3. ✅ Go to Tenants section
4. ✅ Create tenant
5. ✅ Select avatar (voice inherited)
6. ✅ See avatar preview with voice info
7. ✅ Create tenant
8. ✅ Tenant list shows avatar with gender

## Confirmation

The voice configuration fields ARE present in the HTML file at:
```
e:\AI_INFLUC_ SAAS\voice-agent-per_db(gpt-auido-mini)\admin\index.html
```

Lines containing voice configuration:
- Line 107-112: Gender dropdown
- Line 113-118: Voice Model dropdown
- Line 238-246: loadVoicesByGender() function
- Line 248-253: showAvatarForm() function
- Line 265-278: createAvatar() function with voice_name

If you still can't see the fields, please:
1. Hard refresh browser (Ctrl + Shift + F5)
2. Clear all browser cache
3. Try incognito/private window
4. Check browser console for errors
