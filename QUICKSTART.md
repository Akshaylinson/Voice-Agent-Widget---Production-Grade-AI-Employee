# 🚀 Quick Start Guide

## Prerequisites
- Docker Desktop installed and running
- OpenAI API key

## Step 1: Configure Environment (2 minutes)

1. Copy environment template:
```bash
copy .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
JWT_SECRET=my-secret-key-123
```

## Step 2: Deploy First Client (3 minutes)

Run deployment script:

**Windows:**
```cmd
deploy-client.bat client1 8001
```

**Linux/Mac:**
```bash
chmod +x deploy-client.sh
./deploy-client.sh client1 8001
```

Wait for containers to start (30-60 seconds).

## Step 3: Configure Voice Agent (5 minutes)

1. Open admin dashboard: http://localhost:3000

2. Fill in configuration:
   - **Company Name**: Your Company Name
   - **Avatar URL**: (optional) https://your-domain.com/avatar.png
   - **Introduction Script**: 
     ```
     Hello! I'm your AI assistant from [Company Name]. 
     I can help answer questions about our services and company. 
     What would you like to know?
     ```
   - **Voice Model**: Select preferred voice (alloy recommended)

3. Click "Save Configuration"

## Step 4: Add Knowledge (5 minutes)

Add at least 3-5 knowledge entries:

**Example 1:**
- Category: company_overview
- Title: About Our Company
- Content: We are a leading technology company specializing in AI solutions. Founded in 2020, we help businesses automate customer engagement.

**Example 2:**
- Category: services
- Title: AI Voice Agents
- Content: Our AI voice agents provide 24/7 customer support, answer questions, and guide visitors through your services using natural voice conversation.

**Example 3:**
- Category: pricing
- Title: Pricing Plans
- Content: We offer three plans: Starter at $99/month, Professional at $299/month, and Enterprise with custom pricing. All plans include unlimited conversations.

**Example 4:**
- Category: contact
- Title: Contact Information
- Content: You can reach us at support@company.com or call 1-800-123-4567. Our office hours are Monday to Friday, 9 AM to 6 PM EST.

## Step 5: Test Widget (2 minutes)

1. Open demo page: `demo.html` in your browser

2. Click the floating avatar in bottom-right corner

3. Allow microphone access when prompted

4. Listen to introduction, then speak your question

5. Wait for AI response

## Step 6: Embed on Your Website (1 minute)

Add this code before closing `</body>` tag on your website:

```html
<script>
window.VOICE_AGENT_API_URL = 'http://localhost:8001/api';
</script>
<script src="http://localhost:8001/voice-agent-widget.js"></script>
```

**For production, replace localhost with your domain:**
```html
<script>
window.VOICE_AGENT_API_URL = 'https://voice-api.yourdomain.com/api';
</script>
<script src="https://voice-api.yourdomain.com/voice-agent-widget.js"></script>
```

## ✅ You're Done!

Your voice agent is now live and ready to interact with visitors.

## 🎯 Test Questions to Try

- "What services do you offer?"
- "Tell me about your company"
- "What are your pricing plans?"
- "How can I contact you?"
- "What are your business hours?"

## 🔧 Troubleshooting

**Widget not appearing?**
- Check browser console for errors
- Verify API URL is correct
- Ensure Docker containers are running: `docker ps`

**Microphone not working?**
- Use HTTPS (required for microphone access)
- Check browser permissions
- Try different browser (Chrome/Edge recommended)

**No response from agent?**
- Verify OpenAI API key is valid
- Check you added knowledge entries
- View logs: `docker logs voice-agent-client1`

**Database connection error?**
- Wait 30 seconds for PostgreSQL to initialize
- Restart containers: `docker-compose restart`

## 📊 View Analytics

Access conversation logs and analytics:
http://localhost:3000 → Conversations tab

## 🚀 Deploy Additional Clients

Deploy isolated instances for other clients:

```cmd
deploy-client.bat client2 8002
deploy-client.bat client3 8003
```

Each client gets:
- Separate database
- Independent configuration
- Isolated knowledge base
- Unique embed code

## 📞 Support

For issues or questions, check:
- README.md for detailed documentation
- Docker logs: `docker logs voice-agent-client1`
- Backend logs: `docker logs db-client1`

---

**Total Setup Time: ~15-20 minutes**
