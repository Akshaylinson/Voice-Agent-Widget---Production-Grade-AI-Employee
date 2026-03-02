# Voice Agent Widget - Production-Grade AI Employee

A fully containerized, embeddable voice-only conversational AI assistant designed for multi-client SaaS deployment with complete data isolation.

## 🎯 Features

- **Voice-Only Interaction**: No text chat, pure voice conversation
- **Auto-Introduction**: Plays custom greeting on every widget activation
- **Auto-Listening**: Starts recording automatically after introduction
- **Isolated Backend**: Each client has dedicated database and infrastructure
- **Structured Knowledge**: Admin-managed company knowledge base
- **Conversation Logging**: Full analytics and conversation history
- **Brand Customization**: Custom avatar, colors, voice, and introduction
- **Mobile Responsive**: Works seamlessly on desktop and mobile
- **Containerized**: Docker-based deployment for easy scaling
- **Multi-Language Support**: Configurable language detection

## 🏗️ Architecture

```
┌─────────────────┐
│  Client Website │
│   + Widget JS   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Voice Agent Backend (Client1)   │
│  ┌──────────┐      ┌─────────────┐ │
│  │ FastAPI  │◄────►│ PostgreSQL  │ │
│  │  + AI    │      │  (Isolated) │ │
│  └──────────┘      └─────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     Voice Agent Backend (Client2)   │
│  ┌──────────┐      ┌─────────────┐ │
│  │ FastAPI  │◄────►│ PostgreSQL  │ │
│  │  + AI    │      │  (Isolated) │ │
│  └──────────┘      └─────────────┘ │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
voice-agent-per_db/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # DB connection
│   ├── voice_service.py     # OpenAI voice processing
│   └── knowledge_service.py # Knowledge retrieval
├── admin/
│   ├── Dockerfile
│   └── index.html           # Admin dashboard
├── widget/
│   ├── index.html           # Standalone widget demo
│   └── voice-agent-widget.js # Embeddable widget
├── docker-compose.yml       # Default deployment
├── deploy-client.sh         # Linux/Mac deployment script
├── deploy-client.bat        # Windows deployment script
└── .env.example             # Environment template
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- Modern browser with microphone access

### 1. Clone and Configure

```bash
cd voice-agent-per_db
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET=your-secret-here
```

### 2. Deploy First Client

**Linux/Mac:**
```bash
chmod +x deploy-client.sh
./deploy-client.sh client1 8001
```

**Windows:**
```cmd
deploy-client.bat client1 8001
```

### 3. Access Admin Dashboard

Open: `http://localhost:3000`

Configure:
- Company name
- Avatar image URL
- Introduction script
- Voice model (alloy, echo, fable, onyx, nova, shimmer)
- Add knowledge entries

### 4. Embed Widget on Client Website

Add before closing `</body>` tag:

```html
<script>
window.VOICE_AGENT_API_URL = 'http://localhost:8001/api';
</script>
<script src="http://localhost:8001/voice-agent-widget.js"></script>
```

## 🎨 Widget Customization

### Avatar Image
Upload your company logo or AI persona image, then add URL in admin dashboard.

### Brand Colors
Configure in admin dashboard:
```json
{
  "primary": "#4F46E5",
  "secondary": "#818CF8"
}
```

### Introduction Script
Example:
```
Hello! I'm Sarah, your AI assistant from Acme Corp. 
I can help you with our services, pricing, and answer 
any questions about our company. How can I assist you today?
```

### Voice Models
- **alloy**: Neutral, balanced
- **echo**: Clear, professional
- **fable**: Warm, friendly
- **onyx**: Deep, authoritative
- **nova**: Energetic, modern
- **shimmer**: Soft, gentle

## 📊 Knowledge Base Structure

Add structured knowledge through admin dashboard:

### Categories
- **company_overview**: About us, mission, history
- **services**: Service descriptions, features
- **products**: Product details, specifications
- **pricing**: Plans, costs, packages
- **faq**: Common questions and answers
- **policies**: Terms, privacy, refunds
- **contact**: Support info, locations, hours

### Example Entry
```
Category: services
Title: Web Development Services
Content: We offer full-stack web development including 
React, Node.js, and cloud deployment. Our team builds 
scalable, secure web applications with modern technologies.
```

## 🔒 Security & Isolation

### Per-Client Isolation
- Dedicated Docker container
- Isolated PostgreSQL database
- Separate network namespace
- Independent configuration

### Data Privacy
- Voice recordings processed securely
- Transcripts stored in client's database only
- No cross-tenant data access
- Configurable retention policies

## 📈 Analytics & Monitoring

Access conversation logs in admin dashboard:
- User queries (transcribed)
- Agent responses
- Conversation duration
- Session tracking
- Frequently asked questions

## 🌐 Multi-Client Deployment

Deploy multiple isolated clients:

```bash
# Client 1
./deploy-client.sh client1 8001

# Client 2
./deploy-client.sh client2 8002

# Client 3
./deploy-client.sh client3 8003
```

Each client gets:
- Unique API endpoint
- Isolated database
- Independent configuration
- Separate widget embed code

## 🛠️ API Endpoints

### Configuration
- `GET /api/config` - Get client configuration
- `POST /api/config` - Update configuration

### Voice Interaction
- `GET /api/introduction` - Get introduction audio
- `POST /api/voice-query` - Process voice query

### Knowledge Management
- `GET /api/knowledge` - List all knowledge
- `POST /api/knowledge` - Add knowledge entry

### Analytics
- `GET /api/conversations` - Get conversation history

### Health Check
- `GET /health` - Service health status

## 🎯 Widget Behavior

1. **Idle State**: Floating avatar visible
2. **Click to Activate**: User clicks avatar
3. **Auto-Introduction**: Plays custom greeting
4. **Auto-Listening**: Starts recording after intro
5. **Silence Detection**: Auto-stops after 10 seconds
6. **Processing**: Sends audio to backend
7. **Response Playback**: Plays AI response
8. **Continuous Loop**: Returns to listening
9. **Click to Deactivate**: Stops all activity

## 🔧 Development

### Run Backend Locally
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/voice_agent"
export OPENAI_API_KEY="your-key"
export CLIENT_ID="dev_client"
uvicorn main:app --reload --port 8000
```

### Test Widget
Open `widget/index.html` in browser with local backend running.

## 📦 Production Deployment

### Cloud Deployment (AWS/GCP/Azure)
1. Build and push Docker images to registry
2. Deploy containers with orchestration (ECS/GKE/AKS)
3. Use managed PostgreSQL (RDS/Cloud SQL/Azure DB)
4. Configure load balancer and SSL
5. Set environment variables securely

### Scaling Considerations
- Use container orchestration (Kubernetes/ECS)
- Implement Redis for session management
- Add CDN for widget delivery
- Enable database replication
- Implement rate limiting

## 🐛 Troubleshooting

### Widget Not Loading
- Check CORS configuration
- Verify API_URL is correct
- Check browser console for errors

### Microphone Not Working
- Ensure HTTPS (required for mic access)
- Check browser permissions
- Verify getUserMedia support

### No Response from Agent
- Verify OpenAI API key is valid
- Check knowledge base has entries
- Review backend logs: `docker logs voice-agent-client1`

### Database Connection Issues
- Ensure PostgreSQL container is running
- Check DATABASE_URL environment variable
- Verify network connectivity

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For deployment assistance or customization requests, contact your system administrator.

---

**Built with**: FastAPI, OpenAI GPT-4o-mini, Whisper, TTS, PostgreSQL, Docker
