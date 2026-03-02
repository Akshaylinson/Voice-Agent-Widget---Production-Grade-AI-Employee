# 📡 API Documentation

## Base URL

```
Development: http://localhost:8001/api
Production: https://voice-api.yourdomain.com/api
```

## Authentication

Currently, the API is open for widget integration. For production, implement API key authentication for admin endpoints.

## Endpoints

### Configuration

#### Get Client Configuration
```http
GET /api/config
```

**Response:**
```json
{
  "id": 1,
  "client_id": "client1",
  "company_name": "Demo Company",
  "avatar_url": "https://example.com/avatar.png",
  "introduction_script": "Hello! I'm your AI assistant...",
  "voice_model": "alloy",
  "brand_colors": {
    "primary": "#4F46E5",
    "secondary": "#818CF8"
  },
  "supported_languages": ["en"],
  "widget_position": "bottom-right",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Update Client Configuration
```http
POST /api/config
Content-Type: application/json
```

**Request Body:**
```json
{
  "company_name": "Acme Corp",
  "avatar_url": "https://acme.com/avatar.png",
  "introduction_script": "Hello! I'm Sarah from Acme Corp...",
  "voice_model": "nova",
  "brand_colors": {
    "primary": "#FF6B6B",
    "secondary": "#4ECDC4"
  },
  "supported_languages": ["en", "es"]
}
```

**Response:** Updated configuration object

---

### Voice Interaction

#### Get Introduction Audio
```http
GET /api/introduction
```

**Response:** Audio file (audio/mpeg)

**Headers:**
- `Content-Type: audio/mpeg`

---

#### Process Voice Query
```http
POST /api/voice-query
Content-Type: multipart/form-data
```

**Request:**
- `audio` (file): Audio file in webm format
- `session_id` (optional): Session identifier for conversation continuity

**Response:** Audio file (audio/mpeg)

**Headers:**
- `Content-Type: audio/mpeg`
- `X-Transcript: <response_text>`
- `X-Session-ID: <session_id>`

**Example using JavaScript:**
```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'query.webm');
formData.append('session_id', sessionId);

const response = await fetch('http://localhost:8001/api/voice-query', {
  method: 'POST',
  body: formData
});

const transcript = response.headers.get('X-Transcript');
const newSessionId = response.headers.get('X-Session-ID');
const audioBlob = await response.blob();
```

---

### Knowledge Management

#### List All Knowledge
```http
GET /api/knowledge
```

**Response:**
```json
[
  {
    "id": 1,
    "client_id": "client1",
    "category": "services",
    "title": "Web Development",
    "content": "We offer full-stack web development...",
    "metadata": null,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Add Knowledge Entry
```http
POST /api/knowledge
Content-Type: application/json
```

**Request Body:**
```json
{
  "category": "pricing",
  "title": "Pricing Plans",
  "content": "We offer three plans: Starter at $99/month...",
  "metadata": {
    "tags": ["pricing", "plans"],
    "priority": "high"
  }
}
```

**Response:** Created knowledge object

**Categories:**
- `company_overview`
- `services`
- `products`
- `pricing`
- `faq`
- `policies`
- `contact`

---

### Analytics

#### Get Conversation History
```http
GET /api/conversations?limit=50
```

**Query Parameters:**
- `limit` (optional): Number of conversations to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "client_id": "client1",
    "session_id": "abc-123",
    "user_query": "What services do you offer?",
    "user_query_audio_url": null,
    "agent_response": "We offer web development, mobile apps...",
    "agent_response_audio_url": null,
    "language": "en",
    "duration_ms": 2500,
    "created_at": "2024-01-01T12:00:00"
  }
]
```

---

### Health Check

#### Service Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "client_id": "client1"
}
```

---

### Widget File

#### Get Widget JavaScript
```http
GET /voice-agent-widget.js
```

**Response:** JavaScript file

**Headers:**
- `Content-Type: application/javascript`
- `Access-Control-Allow-Origin: *`

---

## Voice Models

Available OpenAI TTS voices:

| Voice | Description | Best For |
|-------|-------------|----------|
| `alloy` | Neutral, balanced | General purpose |
| `echo` | Clear, professional | Business, corporate |
| `fable` | Warm, friendly | Customer service |
| `onyx` | Deep, authoritative | Professional services |
| `nova` | Energetic, modern | Tech, startups |
| `shimmer` | Soft, gentle | Healthcare, wellness |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

Currently no rate limits implemented. For production:
- Recommended: 100 requests per minute per client
- Voice queries: 20 per minute per session
- Knowledge updates: 10 per minute

---

## CORS Configuration

Development: All origins allowed (`*`)

Production: Configure specific domains:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## WebSocket Support (Future)

For real-time voice streaming:

```javascript
const ws = new WebSocket('wss://voice-api.yourdomain.com/ws/voice');

ws.onopen = () => {
  // Send audio chunks
  ws.send(audioChunk);
};

ws.onmessage = (event) => {
  // Receive audio response
  const audioChunk = event.data;
};
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
class VoiceAgentClient {
  constructor(private apiUrl: string) {}

  async getConfig() {
    const response = await fetch(`${this.apiUrl}/config`);
    return response.json();
  }

  async processVoiceQuery(audioBlob: Blob, sessionId?: string) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'query.webm');
    if (sessionId) formData.append('session_id', sessionId);

    const response = await fetch(`${this.apiUrl}/voice-query`, {
      method: 'POST',
      body: formData
    });

    return {
      audio: await response.blob(),
      transcript: response.headers.get('X-Transcript'),
      sessionId: response.headers.get('X-Session-ID')
    };
  }

  async addKnowledge(data: {
    category: string;
    title: string;
    content: string;
  }) {
    const response = await fetch(`${this.apiUrl}/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}

// Usage
const client = new VoiceAgentClient('http://localhost:8001/api');
const config = await client.getConfig();
```

### Python

```python
import requests

class VoiceAgentClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
    
    def get_config(self):
        response = requests.get(f"{self.api_url}/config")
        return response.json()
    
    def process_voice_query(self, audio_file, session_id=None):
        files = {'audio': ('query.webm', audio_file, 'audio/webm')}
        data = {'session_id': session_id} if session_id else {}
        
        response = requests.post(
            f"{self.api_url}/voice-query",
            files=files,
            data=data
        )
        
        return {
            'audio': response.content,
            'transcript': response.headers.get('X-Transcript'),
            'session_id': response.headers.get('X-Session-ID')
        }
    
    def add_knowledge(self, category: str, title: str, content: str):
        response = requests.post(
            f"{self.api_url}/knowledge",
            json={
                'category': category,
                'title': title,
                'content': content
            }
        )
        return response.json()

# Usage
client = VoiceAgentClient('http://localhost:8001/api')
config = client.get_config()
```

---

## Testing with cURL

### Get Configuration
```bash
curl http://localhost:8001/api/config
```

### Update Configuration
```bash
curl -X POST http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "introduction_script": "Hello from Test Corp!"
  }'
```

### Add Knowledge
```bash
curl -X POST http://localhost:8001/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "category": "services",
    "title": "Consulting",
    "content": "We provide expert consulting services..."
  }'
```

### Process Voice Query
```bash
curl -X POST http://localhost:8001/api/voice-query \
  -F "audio=@query.webm" \
  -o response.mp3
```

---

## Postman Collection

Import this collection for easy API testing:

```json
{
  "info": {
    "name": "Voice Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Config",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/config"
      }
    },
    {
      "name": "Add Knowledge",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/knowledge",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"category\": \"services\",\n  \"title\": \"Example\",\n  \"content\": \"Example content\"\n}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8001/api"
    }
  ]
}
```

---

## OpenAPI/Swagger Documentation

Access interactive API documentation:

```
http://localhost:8001/docs
```

This provides:
- Interactive API testing
- Request/response schemas
- Authentication details
- Example requests

---

## Support

For API issues or feature requests:
- Check logs: `docker logs voice-agent-client1`
- Review documentation: README.md
- Test endpoints: http://localhost:8001/docs
