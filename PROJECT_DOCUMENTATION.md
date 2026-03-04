# Voice Agent Platform - Complete Project Documentation

## 🎯 Project Overview
Multi-tenant voice-only conversational AI assistant powered by Google Gemini Live API with RAG (Retrieval-Augmented Generation) for SaaS deployment with complete data isolation.

---

## 📐 Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT WEBSITES                          │
│              (Embedded Widget JavaScript)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MASTER ADMIN DASHBOARD                         │
│         (Nginx - Port 3000 - index.html)                   │
│  - Tenant Management                                        │
│  - Avatar Gallery Management                                │
│  - Tenant Dashboard Access                                  │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI - Port 8000)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Admin Endpoints (/admin/*)                          │  │
│  │  - Tenant CRUD                                        │  │
│  │  - Avatar CRUD                                        │  │
│  │  - Knowledge Base Management                         │  │
│  │  - Voice Configuration                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Public API Endpoints (/api/*)                       │  │
│  │  - Widget Configuration                              │  │
│  │  - Voice Query Processing                            │  │
│  │  - Introduction Audio                                │  │
│  │  - Knowledge Retrieval                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                            │  │
│  │  - Gemini Live Session (LLM + RAG)                   │  │
│  │  - Google Cloud TTS                                  │  │
│  │  - Tenant Middleware (Authentication)                │  │
│  │  - Encryption Service                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           PostgreSQL Database (Port 5432)                   │
│  - Tenants Table                                            │
│  - Avatars Table                                            │
│  - Knowledge Base Table (with pgvector)                     │
│  - Conversations Table                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### 1. Tenants Table
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    avatar_id UUID REFERENCES avatars(id),
    introduction_script TEXT,
    voice_tone VARCHAR(50) DEFAULT 'friendly',
    speaking_rate FLOAT DEFAULT 1.0,
    pitch FLOAT DEFAULT 0.0,
    volume FLOAT DEFAULT 1.0,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 500,
    gemini_api_key_encrypted TEXT,
    status VARCHAR(20) DEFAULT 'active',
    brand_colors JSON,
    widget_signature VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Avatars Table
```sql
CREATE TABLE avatars (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) NOT NULL DEFAULT 'female',
    image_data TEXT NOT NULL,  -- Base64 encoded image
    voice_provider VARCHAR(50) DEFAULT 'google',
    voice_name VARCHAR(100) DEFAULT 'en-US-Neural2-F',
    browser_voice_name VARCHAR(100),  -- Fallback browser TTS voice
    personality_prompt TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Knowledge Base Table
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768),  -- pgvector for RAG
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tenant_id ON knowledge_base(tenant_id);
```

### 4. Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    transcript TEXT,
    response TEXT,
    token_usage INTEGER,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tenant_session ON conversations(tenant_id, session_id);
```

---

## 🎭 Module 1: Master Admin Dashboard

### Location: `/admin/index.html`

### Features:

#### 1.1 Tenant Management
- **Create Tenant**
  - Company name
  - Domain
  - Avatar selection (dropdown)
  - Introduction script
  - Auto-generates widget signature
  - Returns embed code

- **List Tenants**
  - Display all tenants in table
  - Show: Company, Domain, Avatar, Status
  - Dashboard button (opens tenant-dashboard.html)

- **Tenant Status**
  - Active/Suspended toggle

#### 1.2 Avatar Gallery Management
- **Create Avatar**
  - Avatar name
  - Gender (Male/Female)
  - Google Cloud TTS voice selection (gender-filtered)
  - Browser TTS voice selection (fallback)
  - Image upload (converted to base64)
  - Preview before creation

- **List Avatars**
  - Grid display with avatar cards
  - Show: Image, Name, Gender, Voice
  - Edit and Delete buttons

- **Edit Avatar**
  - Modal popup with current data pre-filled
  - Update name, gender, voices
  - Optional image replacement
  - Voice dropdown updates on gender change

- **Delete Avatar**
  - Confirmation modal
  - Prevents deletion if assigned to tenants

#### 1.3 Voice Configuration
- **Google Cloud TTS Voices**
  - Female: Neural2-C, E, F, G, H, Studio-O
  - Male: Neural2-A, D, I, J, Studio-M
  - Gender-filtered dropdown

- **Browser TTS Voices**
  - Auto-populated from browser's speechSynthesis API
  - Shows voice name and language
  - Used as fallback when Google TTS fails

### API Endpoints Used:
```
POST   /admin/tenants
GET    /admin/tenants
GET    /admin/tenant/{id}
PUT    /admin/tenant/{id}

POST   /admin/avatars
GET    /admin/avatars
PUT    /admin/avatars/{id}
DELETE /admin/avatars/{id}

GET    /admin/voices
```

---

## 🎛️ Module 2: Tenant Dashboard

### Location: `/admin/tenant-dashboard.html`

### Features:

#### 2.1 Tenant Overview
- Company name
- Domain
- Status badge
- Widget embed code (copy button)
- Analytics:
  - Total conversations
  - Total tokens used
  - Last activity timestamp

#### 2.2 Configuration Management
- **Avatar Selection**
  - Dropdown with avatar preview
  - Shows current avatar image

- **Introduction Script**
  - Textarea for custom greeting
  - Played on widget activation

- **Voice Settings**
  - Voice tone (friendly, professional, etc.)
  - Speaking rate (0.5 - 2.0)
  - Pitch (-20 to +20)
  - Volume (0.0 - 1.0)

- **AI Settings**
  - Temperature (0.0 - 1.0)
  - Max tokens (100 - 2000)
  - Gemini API key (encrypted)

- **Brand Colors**
  - Primary color picker
  - Secondary color picker
  - Applied to widget

#### 2.3 Knowledge Base Management
- **Add Knowledge**
  - Category selection (company_overview, services, products, pricing, faq, policies, contact)
  - Title
  - Content (textarea)
  - Auto-generates embeddings for RAG

- **List Knowledge**
  - Table view with category, title, content
  - Edit and Delete buttons
  - Active/Inactive toggle

- **Edit Knowledge**
  - Update category, title, content
  - Re-generates embeddings

#### 2.4 Conversation History
- **View Conversations**
  - Table with transcript, response, timestamp
  - Paginated (limit 50)
  - Sorted by most recent

### API Endpoints Used:
```
GET    /admin/tenant/{id}
PUT    /admin/tenant/{id}
GET    /admin/tenant/{id}/knowledge
POST   /admin/tenant/{id}/knowledge
PUT    /admin/tenant/{id}/knowledge/{kid}
DELETE /admin/tenant/{id}/knowledge/{kid}
GET    /admin/avatars
```

---

## 🎤 Module 3: Voice Agent Widget

### Location: `/widget/voice-agent-widget.js`

### Features:

#### 3.1 Widget Initialization
- Loads configuration from API
- Creates floating avatar button
- Applies brand colors
- Displays avatar image

#### 3.2 Voice Interaction Flow
1. **User clicks avatar** → Widget activates
2. **Play introduction** → Google Cloud TTS (or browser TTS fallback)
3. **Auto-start listening** → Browser Speech Recognition API
4. **User speaks** → Transcript captured
5. **Send to backend** → Gemini LLM processes with RAG
6. **Receive response** → Google Cloud TTS (or browser TTS fallback)
7. **Play response** → Audio playback
8. **Loop back to listening** → Continuous conversation
9. **User clicks avatar again** → Deactivate

#### 3.3 Speech Recognition
- Uses browser's Web Speech API
- `webkitSpeechRecognition` or `SpeechRecognition`
- Language: en-US (configurable)
- Continuous: false
- Interim results: false

#### 3.4 Audio Playback
- **Primary: Google Cloud TTS**
  - Receives audio blob from backend
  - Plays using HTML5 Audio API
  - Shows speaking animation

- **Fallback: Browser TTS**
  - Uses `speechSynthesis` API
  - Applies selected browser voice
  - Triggered when backend returns text instead of audio

#### 3.5 Visual States
- **Idle**: Static avatar with green status dot
- **Listening**: Pulsing animation, red status dot
- **Speaking**: Scale animation, green status dot

#### 3.6 Authentication
- Tenant ID (from embed code)
- Widget signature (from embed code)
- Sent in headers: `X-Tenant-ID`, `X-Signature`

### Embed Code:
```html
<script>
window.VOICE_AGENT_TENANT_ID = "{tenant_id}";
window.VOICE_AGENT_SIGNATURE = "{signature}";
window.VOICE_AGENT_API_URL = "http://localhost:8000/api";
</script>
<script src="http://localhost:8000/voice-agent-widget.js"></script>
```

### API Endpoints Used:
```
GET  /api/config
GET  /api/introduction
POST /api/voice-query
```

---

## 🔧 Module 4: Backend Services

### 4.1 Tenant Middleware (`tenant_middleware.py`)
- **Authentication**
  - Validates `X-Tenant-ID` and `X-Signature` headers
  - Retrieves tenant from database
  - Decrypts Gemini API key
  - Attaches tenant to request context

- **Encryption**
  - Uses Fernet symmetric encryption
  - Encrypts/decrypts Gemini API keys
  - Key stored in environment variable

### 4.2 Gemini Service (`gemini_service.py`)
- **GeminiLiveSession Class**
  - Initializes Gemini model
  - Manages conversation context
  - Processes text queries
  - Integrates RAG for knowledge retrieval

- **RAG Implementation**
  - Generates embeddings using Gemini
  - Stores in pgvector
  - Retrieves relevant knowledge based on query
  - Injects context into LLM prompt

- **Knowledge Embedding**
  - Async function to generate embeddings
  - Uses `models/embedding-001`
  - Stores 768-dimensional vectors

### 4.3 Google TTS Service (`google_tts_service.py`)
- **GoogleTTSService Class**
  - `generate_audio()` method
  - Parameters:
    - text: Content to synthesize
    - voice_name: Google Cloud voice
    - gender: MALE/FEMALE
    - speaking_rate: Speed (0.25 - 4.0)
    - pitch: Tone (-20.0 - 20.0)
  - Returns: MP3 audio bytes
  - Error handling with fallback

### 4.4 Database Service (`database.py`)
- **init_db()**
  - Enables pgvector extension
  - Creates all tables
  - Runs migrations (browser_voice_name column)

- **get_db()**
  - Dependency injection for FastAPI
  - Session management
  - Auto-closes connections

---

## 🔌 API Endpoints Reference

### Admin Endpoints (Master Admin Only)

#### Tenant Management
```
POST   /admin/tenants
Body: {
  company_name: string,
  domain: string,
  avatar_id?: string,
  introduction_script?: string,
  gemini_api_key?: string,
  speaking_rate?: float,
  pitch?: float
}
Response: {
  tenant_id: string,
  widget_signature: string,
  embed_code: string
}

GET    /admin/tenants
Response: [{ id, company_name, domain, avatar_id, status, created_at }]

GET    /admin/tenant/{tenant_id}
Response: {
  id, company_name, domain, avatar_id, avatar_url,
  introduction_script, voice_tone, speaking_rate, pitch,
  volume, temperature, max_tokens, status, brand_colors,
  widget_signature, created_at, analytics: { ... }
}

PUT    /admin/tenant/{tenant_id}
Body: {
  company_name?, domain?, avatar_id?, introduction_script?,
  voice_tone?, speaking_rate?, pitch?, volume?,
  temperature?, max_tokens?, gemini_api_key?, brand_colors?
}
Response: { status: "updated" }
```

#### Avatar Management
```
POST   /admin/avatars
FormData: {
  name: string,
  gender: "male" | "female",
  voice_name: string,
  browser_voice_name?: string,
  image_file: File
}
Response: { id, name, gender, voice_name, browser_voice_name }

GET    /admin/avatars
Response: [{
  id, name, gender, voice_name, browser_voice_name,
  voice_provider, image_data
}]

PUT    /admin/avatars/{avatar_id}
FormData: {
  name: string,
  gender: "male" | "female",
  voice_name: string,
  browser_voice_name?: string,
  image_file?: File
}
Response: { status: "updated", id, name, gender, voice_name, browser_voice_name }

DELETE /admin/avatars/{avatar_id}
Response: { status: "deleted" }
```

#### Knowledge Management
```
GET    /admin/tenant/{tenant_id}/knowledge
Response: [{ id, category, title, content, is_active }]

POST   /admin/tenant/{tenant_id}/knowledge
Body: { category: string, title: string, content: string }
Response: { status: "created", id: string }

PUT    /admin/tenant/{tenant_id}/knowledge/{knowledge_id}
Body: { category?, title?, content?, is_active? }
Response: { status: "updated" }

DELETE /admin/tenant/{tenant_id}/knowledge/{knowledge_id}
Response: { status: "deleted" }
```

#### Voice Configuration
```
GET    /admin/voices?gender={male|female}
Response: {
  female: [{ name, label }],
  male: [{ name, label }]
}
```

### Public API Endpoints (Widget)

#### Configuration
```
GET    /api/config
Headers: { X-Tenant-ID, X-Signature }
Response: {
  company_name: string,
  avatar_url: string,
  introduction_script: string,
  avatar_gender: string,
  voice_name: string,
  browser_voice_name: string,
  brand_colors: { primary, secondary }
}
```

#### Voice Interaction
```
GET    /api/introduction
Headers: { X-Tenant-ID, X-Signature }
Response: Audio blob (audio/mpeg) OR { text: string }

POST   /api/voice-query
Headers: { X-Tenant-ID, X-Signature }
FormData: { transcript: string, session_id?: string }
Response: Audio blob (audio/mpeg) OR { response: string, session_id: string }
```

---

## 🔐 Security Features

### 1. Data Isolation
- Each tenant has isolated data in shared database
- Tenant ID filtering on all queries
- Widget signature validation

### 2. API Key Encryption
- Gemini API keys encrypted with Fernet
- Encryption key stored in environment variable
- Decrypted only when needed

### 3. Authentication
- Widget signature generated on tenant creation
- SHA256 hash of UUID
- Validated on every widget API call

### 4. CORS
- Configured to allow all origins (configurable)
- Can be restricted to specific domains

---

## 🚀 Deployment

### Docker Compose Structure
```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    ports: 5432:5432
    environment:
      POSTGRES_DB: voice_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports: 8000:8000
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/voice_agent
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    depends_on:
      - db

  admin:
    build: ./admin
    ports: 3000:80
    depends_on:
      - backend
```

### Environment Variables
```
GEMINI_API_KEY=your-gemini-api-key
ENCRYPTION_KEY=your-fernet-encryption-key
DATABASE_URL=postgresql://postgres:postgres@db:5432/voice_agent
```

---

## 📦 Project Structure

```
voice-agent-per_db/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # FastAPI app with all endpoints
│   ├── models.py                  # SQLAlchemy models
│   ├── database.py                # DB connection & migrations
│   ├── config.py                  # Configuration management
│   ├── tenant_middleware.py       # Authentication & encryption
│   ├── gemini_service.py          # Gemini LLM + RAG
│   └── google_tts_service.py      # Google Cloud TTS
│
├── admin/
│   ├── Dockerfile
│   ├── index.html                 # Master admin dashboard
│   └── tenant-dashboard.html      # Individual tenant dashboard
│
├── widget/
│   ├── index.html                 # Standalone widget demo
│   └── voice-agent-widget.js      # Embeddable widget
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🎯 Key Features Summary

### ✅ Multi-Tenancy
- Complete data isolation
- Per-tenant configuration
- Unique widget signatures

### ✅ Voice Interaction
- Browser Speech Recognition (STT)
- Google Cloud TTS (Primary)
- Browser TTS (Fallback)
- Continuous conversation loop

### ✅ AI & RAG
- Google Gemini Live API
- Vector embeddings (pgvector)
- Context-aware responses
- Knowledge base integration

### ✅ Avatar System
- Custom avatar images
- Gender-based voice selection
- Google Cloud TTS voices
- Browser TTS fallback voices

### ✅ Admin Features
- Tenant management
- Avatar gallery
- Knowledge base CRUD
- Conversation analytics
- Brand customization

### ✅ Widget Features
- Embeddable JavaScript
- Auto-introduction
- Auto-listening
- Visual state indicators
- Mobile responsive

---

## 🔄 Data Flow Examples

### Example 1: Widget Initialization
```
1. User embeds widget on website
2. Widget loads → GET /api/config
3. Backend validates tenant credentials
4. Returns: avatar, colors, introduction, voices
5. Widget displays avatar with brand colors
```

### Example 2: Voice Conversation
```
1. User clicks avatar
2. Widget → GET /api/introduction
3. Backend → Google Cloud TTS → Audio
4. Widget plays audio
5. Widget starts listening (Speech Recognition)
6. User speaks: "What are your services?"
7. Widget → POST /api/voice-query (transcript)
8. Backend → Gemini LLM + RAG retrieval
9. Backend → Google Cloud TTS → Audio
10. Widget plays response
11. Loop back to step 5
```

### Example 3: RAG Knowledge Retrieval
```
1. User query: "What is your pricing?"
2. Backend generates query embedding
3. pgvector searches similar knowledge entries
4. Retrieves top 3 relevant entries
5. Injects into Gemini prompt as context
6. Gemini generates response using knowledge
7. Response sent back to widget
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector
- **ORM**: SQLAlchemy
- **AI**: Google Gemini Live API
- **TTS**: Google Cloud Text-to-Speech
- **Encryption**: Cryptography (Fernet)

### Frontend
- **Admin**: HTML + Tailwind CSS + Vanilla JS
- **Widget**: Vanilla JavaScript
- **Speech**: Web Speech API (STT + TTS)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (for admin)
- **Database**: PostgreSQL 16 with pgvector extension

---

## 📝 Migration Notes

### Database Migrations
- Initial schema created via SQLAlchemy
- Manual migration for `browser_voice_name` column
- Auto-runs on startup via `init_db()`

### Migration Script (if needed):
```sql
ALTER TABLE avatars 
ADD COLUMN IF NOT EXISTS browser_voice_name VARCHAR(100);
```

---

## 🐛 Common Issues & Solutions

### Issue 1: ERR_EMPTY_RESPONSE
**Cause**: Backend crashed or not running
**Solution**: Check logs with `docker-compose logs backend`

### Issue 2: CORS Errors
**Cause**: Accessing from different origin
**Solution**: Use `localhost:3000` not `127.0.0.1:5501`

### Issue 3: 404 on tenant-dashboard.html
**Cause**: File not copied to nginx container
**Solution**: Rebuild admin container with updated Dockerfile

### Issue 4: Speech Recognition not working
**Cause**: Browser doesn't support or HTTPS required
**Solution**: Use Chrome/Edge and ensure HTTPS in production

### Issue 5: TTS not playing
**Cause**: Google Cloud TTS failed
**Solution**: Widget automatically falls back to browser TTS

---

## 🎓 Best Practices

### 1. Security
- Always encrypt API keys
- Validate tenant signatures
- Use HTTPS in production
- Implement rate limiting

### 2. Performance
- Cache avatar images
- Limit conversation history queries
- Use connection pooling
- Implement CDN for widget

### 3. Scalability
- Use managed PostgreSQL
- Deploy backend with load balancer
- Implement Redis for sessions
- Use Kubernetes for orchestration

### 4. Monitoring
- Log all API calls
- Track conversation metrics
- Monitor TTS usage
- Alert on errors

---

## 📊 Analytics & Metrics

### Per Tenant
- Total conversations
- Total tokens used
- Last activity timestamp
- Average conversation duration

### System-Wide
- Active tenants count
- Total API calls
- TTS generation time
- Error rates

---

## 🔮 Future Enhancements

### Planned Features
1. Multi-language support
2. Custom voice training
3. Sentiment analysis
4. Real-time streaming (WebSocket)
5. Advanced analytics dashboard
6. A/B testing for introductions
7. Custom widget themes
8. Voice biometrics
9. Integration with CRM systems
10. Mobile SDK

---

## 📞 Support & Maintenance

### Regular Tasks
- Database backups (daily)
- Log rotation (weekly)
- Security updates (monthly)
- Performance optimization (quarterly)

### Monitoring Checklist
- [ ] Backend health endpoint
- [ ] Database connection pool
- [ ] TTS API quota
- [ ] Gemini API quota
- [ ] Disk space
- [ ] Memory usage
- [ ] Response times

---

**Last Updated**: 2026-03-04
**Version**: 3.0 (Gemini Multi-Tenant)
**Status**: Production Ready
