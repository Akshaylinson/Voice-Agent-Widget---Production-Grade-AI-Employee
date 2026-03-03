# Quick Fix for "Domain not authorized" Error

## Problem
Widget shows: `[WIDGET] Config error: {"detail":"Domain not authorized"}`

## Root Cause
The tenant domain in database doesn't match the origin (127.0.0.1:5501)

## Solution Steps

### Step 1: Restart Backend (Apply Code Changes)

The backend code was updated but needs restart:

```bash
# If running with uvicorn directly
# Press Ctrl+C to stop, then:
cd backend
uvicorn main:app --reload --port 8000

# If running with Docker
docker-compose restart backend
```

### Step 2: Update Tenant Domain in Database

**Option A: Using Admin Dashboard (Easiest)**
1. Open: http://localhost:3000
2. Go to Tenants section
3. Find "Codeless AI" tenant
4. Click "Dashboard" or edit button
5. Change domain to: `localhost`
6. Save changes

**Option B: Using SQL (Direct)**

Connect to your database and run:
```sql
UPDATE tenants 
SET domain = 'localhost' 
WHERE id = 'e78f6bbe-4cf0-471c-82cc-20f29a08506f';
```

**Option C: Using Python Script**

If backend is running, use this API call:
```bash
curl -X PUT http://localhost:8000/admin/tenant/e78f6bbe-4cf0-471c-82cc-20f29a08506f \
  -H "Content-Type: application/json" \
  -d '{"domain": "localhost"}'
```

### Step 3: Verify Fix

1. Refresh CodelessAi.html page
2. Open browser console (F12)
3. Look for: `[WIDGET] Config response status: 200` ✅
4. Avatar should appear
5. Introduction should play

### Step 4: If Still Not Working

Check backend logs for the actual origin being sent:
```
[AUTH] Tenant ID: e78f6bbe-4cf0-471c-82cc-20f29a08506f, Signature: 2a8d9cdda05a7648..., Origin: http://127.0.0.1:5501
```

The origin should now be accepted because:
- Domain in DB = `localhost`
- Origin contains `127.0.0.1` (local development)
- Backend allows both ✅

---

## Alternative: Create New Tenant with Correct Domain

If updating is difficult, create a fresh tenant:

1. Open Admin Dashboard: http://localhost:3000
2. Fill form:
   - Company Name: Codeless AI
   - Domain: **localhost** ← Important!
   - OpenAI API Key: (your key)
   - Avatar: (select one)
   - Voice Model: Nova
   - Introduction Script: "Hello! I'm your AI assistant from Codeless AI. How can I help you today?"
3. Click "Create Tenant"
4. Copy the generated embed code
5. Update CodelessAi.html with new tenant ID and signature

---

## Quick Test

After fixing, test the config endpoint directly:

```bash
curl -H "X-Tenant-ID: e78f6bbe-4cf0-471c-82cc-20f29a08506f" \
     -H "X-Signature: 2a8d9cdda05a7648f1e4276c3db042a28659f9cadc016c9761db3a8c17cf1a82" \
     -H "Origin: http://127.0.0.1:5501" \
     http://localhost:8000/api/config
```

Should return:
```json
{
  "company_name": "Codeless AI",
  "avatar_url": "http://localhost:8000/uploads/...",
  "introduction_script": "Hello! I'm your AI assistant...",
  "voice_model": "nova",
  "brand_colors": null
}
```

---

## Checklist

- [ ] Backend restarted (code changes applied)
- [ ] Tenant domain updated to `localhost`
- [ ] Browser cache cleared (Ctrl+Shift+R)
- [ ] Console shows status 200 (not 403)
- [ ] Avatar image visible
- [ ] Introduction plays when clicked

---

## Still Having Issues?

1. **Check backend is running**: http://localhost:8000/health
2. **Check tenant exists**: http://localhost:8000/admin/tenants
3. **Verify domain in database**: Should be `localhost`
4. **Check backend logs**: Look for [AUTH] messages
5. **Try different browser**: Clear cache/cookies
6. **Create new tenant**: With domain = `localhost` from start
