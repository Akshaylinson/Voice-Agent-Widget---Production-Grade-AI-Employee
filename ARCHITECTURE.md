# 🏗️ Gemini Voice Agent - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT WEBSITE                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  <script>                                                   │ │
│  │    window.VOICE_AGENT_TENANT_ID = "uuid";                  │ │
│  │    window.VOICE_AGENT_SIGNATURE = "signature";             │ │
│  │  </script>                                                  │ │
│  │  <script src="voice-agent-widget.js"></script>             │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE AGENT BACKEND                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Server                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │   Auth     │  │   Config   │  │   Voice Query    │   │  │
│  │  │ Middleware │→ │  Endpoint  │  │    Endpoint      │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │         Gemini Service (gemini_service.py)         │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  GeminiLiveSession                           │  │  │  │
│  │  │  │  • Initialize with RAG context               │  │  │  │
│  │  │  │  • Process text queries                      │  │  │  │
│  │  │  │  • Manage conversation state                 │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │                                                     │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  RAG Knowledge Retrieval                     │  │  │  │
│  │  │  │  • Generate query embedding (768-dim)        │  │  │  │
│  │  │  │  • Vector similarity search (pgvector)       │  │  │  │
│  │  │  │  • Retrieve top-K knowledge chunks           │  │  │  │
│  │  │  │  • Inject into Gemini prompt                 │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────┬───────────────────────┘
                    │                     │
                    │                     │
        ┌───────────▼──────────┐  ┌──────▼──────────────────────┐
        │  PostgreSQL + pgvector│  │  Google Gemini API          │
        │  ┌──────────────────┐ │  │  ┌────────────────────────┐│
        │  │   Tenants        │ │  │  │  gemini-2.0-flash-exp  ││
        │  │   • Config       │ │  │  │  • Live conversation   ││
        │  │   • API keys     │ │  │  │  • Context injection   ││
        │  │   • Voice settings│ │  │  └────────────────────────┘│
        │  └──────────────────┘ │  │                             │
        │  ┌──────────────────┐ │  │  ┌────────────────────────┐│
        │  │ Knowledge Base   │ │  │  │  text-embedding-004    ││
        │  │   • Content      │ │  │  │  • 768-dim vectors     ││
        │  │   • Embeddings   │ │  │  │  • Semantic search     ││
        │  │   • Vector index │ │  │  └────────────────────────┘│
        │  └──────────────────┘ │  └─────────────────────────────┘
        │  ┌──────────────────┐ │
        │  │  Conversations   │ │
        │  │   • Transcripts  │ │
        │  │   • Responses    │ │
        │  │   • Analytics    │ │
        │  └──────────────────┘ │
        └──────────────────────┘
```

## Request Flow - Voice Query

```
┌─────────┐
│ Browser │
│ Widget  │
└────┬────┘
     │
     │ 1. User speaks
     ▼
┌─────────────────┐
│ Browser STT     │ (Web Speech API)
│ Transcription   │
└────┬────────────┘
     │
     │ 2. Send transcript
     ▼
┌──────────────────────────────────────────────────────────┐
│ Backend: /api/voice-query                                │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. Authenticate tenant                             │  │
│  │    • Verify tenant_id + signature                  │  │
│  │    • Load tenant configuration                     │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 2. Generate Query Embedding                        │  │
│  │    • Call Gemini text-embedding-004                │  │
│  │    • Get 768-dimensional vector                    │  │
│  │    • Time: ~100ms                                  │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 3. Vector Similarity Search                        │  │
│  │    • Query pgvector with embedding                 │  │
│  │    • Cosine distance calculation                   │  │
│  │    • Retrieve top 5 knowledge entries              │  │
│  │    • Time: <50ms                                   │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 4. Build Context Prompt                            │  │
│  │    • System instruction with company info          │  │
│  │    • Inject retrieved knowledge                    │  │
│  │    • Add conversation history (optional)           │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 5. Call Gemini Live API                            │  │
│  │    • Send query + context                          │  │
│  │    • Model: gemini-2.0-flash-exp                   │  │
│  │    • Generate grounded response                    │  │
│  │    • Time: 500-1500ms                              │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 6. Log Conversation                                │  │
│  │    • Save transcript                               │  │
│  │    • Save response                                 │  │
│  │    • Record metrics                                │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 7. Return Response                                 │  │
│  │    • JSON: { "response": "...", "session_id": ... }│  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ 3. Response text
                       ▼
              ┌─────────────────┐
              │ Browser TTS     │ (Speech Synthesis API)
              │ Audio Playback  │
              └─────────────────┘
```

## RAG Knowledge Retrieval Flow

```
┌──────────────────┐
│  User Query      │
│  "What services  │
│   do you offer?" │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Gemini Embedding API                   │
│  text-embedding-004                     │
│                                         │
│  Input: "What services do you offer?"  │
│  Output: [0.123, -0.456, 0.789, ...]   │
│          (768 dimensions)               │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  PostgreSQL + pgvector                  │
│                                         │
│  SELECT id, title, content              │
│  FROM knowledge_base                    │
│  WHERE tenant_id = ?                    │
│  ORDER BY embedding <=> query_embedding │
│  LIMIT 5;                               │
│                                         │
│  Uses: IVFFlat index                    │
│  Distance: Cosine similarity            │
│  Time: <50ms                            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Retrieved Knowledge (Top 5)            │
│                                         │
│  1. "Web Development Services"          │
│     "We build modern web apps..."       │
│                                         │
│  2. "Mobile App Development"            │
│     "iOS and Android apps..."           │
│                                         │
│  3. "Cloud Solutions"                   │
│     "AWS and Azure deployment..."       │
│                                         │
│  4. "Pricing Plans"                     │
│     "Starting at $99/month..."          │
│                                         │
│  5. "Support Services"                  │
│     "24/7 customer support..."          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Context Injection                      │
│                                         │
│  System Prompt:                         │
│  "You are an AI for Acme Corp.          │
│   Answer ONLY using this knowledge:     │
│                                         │
│   [Retrieved knowledge inserted here]   │
│                                         │
│   User: What services do you offer?"    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Gemini Response                        │
│                                         │
│  "We offer web development, mobile app  │
│   development, and cloud solutions.     │
│   Our web services include modern       │
│   applications built with React and     │
│   Node.js. For mobile, we create iOS    │
│   and Android apps. We also provide     │
│   AWS and Azure cloud deployment."      │
└─────────────────────────────────────────┘
```

## Multi-Tenant Isolation

```
┌─────────────────────────────────────────────────────────┐
│                    Tenant 1: Acme Corp                   │
│  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │  Configuration │  │  Knowledge Base              │  │
│  │  • API Key     │  │  • Web Development           │  │
│  │  • Voice: Puck │  │  • Mobile Apps               │  │
│  │  • Domain      │  │  • Cloud Solutions           │  │
│  └────────────────┘  │  • Embeddings (768-dim)      │  │
│                      └──────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Conversations                                    │  │
│  │  • Session logs                                   │  │
│  │  • Analytics                                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Tenant 2: TechStart                    │
│  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │  Configuration │  │  Knowledge Base              │  │
│  │  • API Key     │  │  • AI Consulting             │  │
│  │  • Voice: Charon│  │  • Data Science              │  │
│  │  • Domain      │  │  • ML Training               │  │
│  └────────────────┘  │  • Embeddings (768-dim)      │  │
│                      └──────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Conversations                                    │  │
│  │  • Session logs                                   │  │
│  │  • Analytics                                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

        ↓ Complete Data Isolation ↓
        • Separate API keys
        • Isolated knowledge bases
        • Independent embeddings
        • Separate conversation logs
        • Domain-based access control
```

## Performance Metrics

```
┌─────────────────────────────────────────────────────┐
│              Request Timeline                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  0ms ────────────────────────────────────────────   │
│       │ Authentication & Tenant Load               │
│  10ms ────────────────────────────────────────────  │
│       │ Generate Query Embedding                   │
│ 110ms ────────────────────────────────────────────  │
│       │ Vector Similarity Search                   │
│ 150ms ────────────────────────────────────────────  │
│       │ Build Context Prompt                       │
│ 160ms ────────────────────────────────────────────  │
│       │                                            │
│       │ Gemini API Call                            │
│       │ (Generate Response)                        │
│       │                                            │
│ 1500ms ───────────────────────────────────────────  │
│       │ Log Conversation                           │
│ 1520ms ───────────────────────────────────────────  │
│       │ Return Response                            │
│ 1530ms ───────────────────────────────────────────  │
│                                                      │
│  Total Latency: ~1.5 seconds ✅                     │
│  Target: <2 seconds                                 │
└─────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                   Frontend                           │
│  • Vanilla JavaScript                               │
│  • Web Speech API (STT)                             │
│  • Speech Synthesis API (TTS)                       │
│  • WebSocket (optional)                             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Backend                            │
│  • FastAPI (Python 3.9+)                            │
│  • Uvicorn (ASGI server)                            │
│  • SQLAlchemy (ORM)                                 │
│  • Pydantic (validation)                            │
│  • Cryptography (encryption)                        │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Database                           │
│  • PostgreSQL 15                                    │
│  • pgvector extension                               │
│  • IVFFlat indexing                                 │
│  • Vector similarity search                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   AI Services                        │
│  • Google Gemini Live API                           │
│  • gemini-2.0-flash-exp (conversation)              │
│  • text-embedding-004 (embeddings)                  │
│  • 768-dimensional vectors                          │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                Infrastructure                        │
│  • Docker containers                                │
│  • Docker Compose                                   │
│  • Nginx (optional)                                 │
│  • Redis (optional caching)                         │
└─────────────────────────────────────────────────────┘
```

---

**Architecture Version**: 3.0-gemini  
**Last Updated**: 2024  
**Status**: Production Ready ✅
