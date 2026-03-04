from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging
import os
import shutil
import json
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

from database import init_db, get_db
from models import Tenant, Avatar, KnowledgeBase, Conversation
from tenant_middleware import get_tenant_context, encrypt_api_key, decrypt_api_key
from gemini_service import (
    GeminiLiveSession,
    retrieve_knowledge_rag,
    generate_knowledge_embedding
)
import hmac
import hashlib

app = FastAPI(title="Multi-Tenant Voice Agent API")

# Ensure uploads directory exists
UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# Mount static files for serving uploaded avatars
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# Pydantic Models
class TenantCreate(BaseModel):
    company_name: str
    domain: str
    gemini_api_key: Optional[str] = None
    avatar_id: Optional[str] = None
    introduction_script: Optional[str] = None
    voice_model: str = "Puck"
    voice_gender: str = "female"
    speaking_rate: float = 1.0

class KnowledgeCreate(BaseModel):
    category: str
    title: str
    content: str

class TextQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

# Master Admin Endpoints (Codeless Only)
@app.post("/admin/tenants")
def create_tenant(tenant_data: TenantCreate, db: Session = Depends(get_db)):
    widget_signature = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    tenant = Tenant(
        company_name=tenant_data.company_name,
        domain=tenant_data.domain,
        avatar_id=tenant_data.avatar_id,
        introduction_script=tenant_data.introduction_script,
        voice_model=tenant_data.voice_model,
        voice_gender=tenant_data.voice_gender,
        speaking_rate=tenant_data.speaking_rate,
        gemini_api_key_encrypted=encrypt_api_key(tenant_data.gemini_api_key) if tenant_data.gemini_api_key else None,
        widget_signature=widget_signature
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return {
        "tenant_id": str(tenant.id),
        "widget_signature": widget_signature,
        "embed_code": f"""<script>
window.VOICE_AGENT_TENANT_ID = "{tenant.id}";
window.VOICE_AGENT_SIGNATURE = "{widget_signature}";
window.VOICE_AGENT_API_URL = "http://localhost:8000/api";
</script>
<script src="https://codeless-tcr.github.io/vvai/widget.js"></script>"""
    }

@app.get("/admin/tenants")
def list_tenants(db: Session = Depends(get_db)):
    tenants = db.query(Tenant).all()
    return [{
        "id": str(t.id), 
        "company_name": t.company_name, 
        "domain": t.domain, 
        "voice_model": t.voice_model,
        "status": t.status,
        "created_at": t.created_at.isoformat()
    } for t in tenants]

@app.get("/admin/tenant/{tenant_id}")
def get_tenant_details(tenant_id: str, db: Session = Depends(get_db)):
    from sqlalchemy import func
    import uuid
    
    try:
        # Convert string to UUID if needed
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        tenant = db.query(Tenant).filter(Tenant.id == tenant_uuid).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tenant ID format")
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    avatar = None
    if tenant.avatar_id:
        try:
            avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
        except Exception as e:
            logger.error(f"Error loading avatar: {e}")
    
    # Get analytics with error handling
    try:
        total_conversations = db.query(Conversation).filter(Conversation.tenant_id == tenant.id).count()
        total_tokens = db.query(func.sum(Conversation.token_usage)).filter(Conversation.tenant_id == tenant.id).scalar() or 0
        last_activity = db.query(Conversation).filter(Conversation.tenant_id == tenant.id).order_by(
            Conversation.created_at.desc()
        ).first()
    except Exception as e:
        logger.error(f"Error loading analytics: {e}")
        total_conversations = 0
        total_tokens = 0
        last_activity = None
    
    return {
        "id": str(tenant.id),
        "company_name": tenant.company_name,
        "domain": tenant.domain,
        "avatar_id": str(tenant.avatar_id) if tenant.avatar_id else None,
        "avatar_url": avatar.image_data if avatar else None,
        "introduction_script": tenant.introduction_script or "",
        "voice_tone": tenant.voice_tone or "friendly",
        "speaking_rate": tenant.speaking_rate or 1.0,
        "pitch": tenant.pitch or 0.0,
        "volume": tenant.volume or 1.0,
        "temperature": tenant.temperature or 0.7,
        "max_tokens": tenant.max_tokens or 500,
        "status": tenant.status,
        "brand_colors": tenant.brand_colors or {},
        "widget_signature": tenant.widget_signature,
        "created_at": tenant.created_at.isoformat(),
        "analytics": {
            "total_conversations": total_conversations,
            "total_tokens": int(total_tokens),
            "last_activity": last_activity.created_at.isoformat() if last_activity else None
        }
    }

class TenantUpdate(BaseModel):
    company_name: Optional[str] = None
    domain: Optional[str] = None
    avatar_id: Optional[str] = None
    introduction_script: Optional[str] = None
    voice_tone: Optional[str] = None
    speaking_rate: Optional[float] = None
    pitch: Optional[float] = None
    volume: Optional[float] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    gemini_api_key: Optional[str] = None
    brand_colors: Optional[dict] = None

@app.put("/admin/tenant/{tenant_id}")
def update_tenant(tenant_id: str, data: TenantUpdate, db: Session = Depends(get_db)):
    import uuid
    
    try:
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        tenant = db.query(Tenant).filter(Tenant.id == tenant_uuid).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tenant ID format")
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    try:
        if data.company_name: tenant.company_name = data.company_name
        if data.domain: tenant.domain = data.domain
        if data.avatar_id: 
            try:
                tenant.avatar_id = uuid.UUID(data.avatar_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid avatar ID format")
        if data.introduction_script is not None: tenant.introduction_script = data.introduction_script
        if data.voice_tone: tenant.voice_tone = data.voice_tone
        if data.speaking_rate is not None: tenant.speaking_rate = data.speaking_rate
        if data.pitch is not None: tenant.pitch = data.pitch
        if data.volume is not None: tenant.volume = data.volume
        if data.temperature is not None: tenant.temperature = data.temperature
        if data.max_tokens: tenant.max_tokens = data.max_tokens
        if data.gemini_api_key: tenant.gemini_api_key_encrypted = encrypt_api_key(data.gemini_api_key)
        if data.brand_colors: tenant.brand_colors = data.brand_colors
        
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/tenant/{tenant_id}/knowledge")
def get_tenant_knowledge(tenant_id: str, db: Session = Depends(get_db)):
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == tenant_id).all()
    return [{"id": str(k.id), "category": k.category, "title": k.title, "content": k.content, "is_active": k.is_active} for k in knowledge]

@app.post("/admin/tenant/{tenant_id}/knowledge")
async def create_tenant_knowledge(tenant_id: str, knowledge: KnowledgeCreate, db: Session = Depends(get_db)):
    entry = KnowledgeBase(
        tenant_id=tenant_id,
        category=knowledge.category,
        title=knowledge.title,
        content=knowledge.content
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    # Generate embedding asynchronously
    try:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        api_key = decrypt_api_key(tenant.gemini_api_key_encrypted) if tenant.gemini_api_key_encrypted else None
        await generate_knowledge_embedding(db, str(entry.id), api_key)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
    
    return {"status": "created", "id": str(entry.id)}

class KnowledgeUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

@app.put("/admin/tenant/{tenant_id}/knowledge/{knowledge_id}")
def update_tenant_knowledge(tenant_id: str, knowledge_id: str, data: KnowledgeUpdate, db: Session = Depends(get_db)):
    entry = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_id,
        KnowledgeBase.tenant_id == tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    if data.category: entry.category = data.category
    if data.title: entry.title = data.title
    if data.content: entry.content = data.content
    if data.is_active is not None: entry.is_active = data.is_active
    
    db.commit()
    return {"status": "updated"}

@app.delete("/admin/tenant/{tenant_id}/knowledge/{knowledge_id}")
def delete_tenant_knowledge(tenant_id: str, knowledge_id: str, db: Session = Depends(get_db)):
    entry = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_id,
        KnowledgeBase.tenant_id == tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    db.delete(entry)
    db.commit()
    return {"status": "deleted"}

@app.put("/admin/tenants/{tenant_id}/status")
def update_tenant_status(tenant_id: str, status: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.status = status
    db.commit()
    return {"status": "updated"}

@app.put("/admin/tenants/{tenant_id}/avatar")
def update_tenant_avatar(tenant_id: str, avatar_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.avatar_id = avatar_id
    db.commit()
    return {"status": "updated"}

# Avatar Management
@app.post("/admin/avatars")
async def create_avatar(
    name: str, 
    gender: str,
    voice_name: str,
    image_file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Create avatar with voice configuration"""
    import base64
    
    # Validate gender
    if gender.lower() not in ["male", "female"]:
        raise HTTPException(status_code=400, detail="Gender must be 'male' or 'female'")
    
    # Read and encode image
    image_bytes = await image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Detect mime type
    content_type = image_file.content_type or 'image/png'
    image_data = f"data:{content_type};base64,{image_base64}"
    
    avatar = Avatar(
        name=name,
        gender=gender.lower(),
        voice_provider="google",
        voice_name=voice_name,
        image_data=image_data
    )
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    return {
        "id": str(avatar.id), 
        "name": avatar.name,
        "gender": avatar.gender,
        "voice_name": avatar.voice_name
    }

@app.get("/admin/avatars")
def list_avatars(db: Session = Depends(get_db)):
    avatars = db.query(Avatar).all()
    return [{
        "id": str(a.id), 
        "name": a.name,
        "gender": a.gender,
        "voice_name": a.voice_name,
        "voice_provider": a.voice_provider,
        "image_data": a.image_data
    } for a in avatars]

class AvatarUpdate(BaseModel):
    name: Optional[str] = None
    image_data: Optional[str] = None
    default_voice: Optional[str] = None

@app.put("/admin/avatar/{avatar_id}")
async def update_avatar(
    avatar_id: str, 
    name: Optional[str] = None,
    gender: Optional[str] = None,
    voice_name: Optional[str] = None,
    image_file: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db)
):
    import base64
    
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    if name:
        avatar.name = name
    
    if gender:
        if gender.lower() not in ["male", "female"]:
            raise HTTPException(status_code=400, detail="Gender must be 'male' or 'female'")
        avatar.gender = gender.lower()
    
    if voice_name:
        avatar.voice_name = voice_name
    
    if image_file:
        image_bytes = await image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        content_type = image_file.content_type or 'image/png'
        avatar.image_data = f"data:{content_type};base64,{image_base64}"
    
    db.commit()
    return {
        "status": "updated", 
        "id": str(avatar.id),
        "gender": avatar.gender,
        "voice_name": avatar.voice_name
    }

@app.delete("/admin/avatar/{avatar_id}")
def delete_avatar(avatar_id: str, db: Session = Depends(get_db)):
    # Check if avatar is assigned to any tenant
    tenant_count = db.query(Tenant).filter(Tenant.avatar_id == avatar_id).count()
    
    if tenant_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Avatar is currently assigned to {tenant_count} tenant(s). Cannot delete."
        )
    
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    db.delete(avatar)
    db.commit()
    return {"status": "deleted"}

@app.get("/admin/voices")
def list_available_voices(gender: Optional[str] = None):
    """List available Google Cloud TTS voices filtered by gender"""
    
    female_voices = [
        {"name": "en-US-Neural2-C", "label": "Neural2-C (Clear, Professional)"},
        {"name": "en-US-Neural2-E", "label": "Neural2-E (Warm, Friendly)"},
        {"name": "en-US-Neural2-F", "label": "Neural2-F (Natural, Conversational)"},
        {"name": "en-US-Neural2-G", "label": "Neural2-G (Energetic, Modern)"},
        {"name": "en-US-Neural2-H", "label": "Neural2-H (Soft, Gentle)"},
        {"name": "en-US-Studio-O", "label": "Studio-O (Premium Female)"},
    ]
    
    male_voices = [
        {"name": "en-US-Neural2-A", "label": "Neural2-A (Deep, Authoritative)"},
        {"name": "en-US-Neural2-D", "label": "Neural2-D (Professional, Clear)"},
        {"name": "en-US-Neural2-I", "label": "Neural2-I (Friendly, Approachable)"},
        {"name": "en-US-Neural2-J", "label": "Neural2-J (Confident, Strong)"},
        {"name": "en-US-Studio-M", "label": "Studio-M (Premium Male)"},
    ]
    
    if gender:
        if gender.lower() == "female":
            return {"voices": female_voices, "gender": "female"}
        elif gender.lower() == "male":
            return {"voices": male_voices, "gender": "male"}
    
    return {
        "female": female_voices,
        "male": male_voices
    }

# Tenant-Aware Public Endpoints
@app.get("/api/config")
async def get_config(request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    
    avatar_data = None
    avatar_gender = "female"
    voice_name = "en-US-Neural2-F"
    
    if tenant.avatar_id:
        avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
        if avatar:
            avatar_data = avatar.image_data
            avatar_gender = avatar.gender or "female"
            voice_name = avatar.voice_name or "en-US-Neural2-F"
    
    return {
        "company_name": tenant.company_name,
        "avatar_url": avatar_data,
        "introduction_script": tenant.introduction_script,
        "avatar_gender": avatar_gender,
        "voice_name": voice_name,
        "brand_colors": tenant.brand_colors
    }

@app.post("/api/text-query")
async def process_text_query(data: TextQuery, request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    session_id = data.session_id or str(uuid.uuid4())
    
    try:
        # Get API key (tenant-specific or master)
        api_key = tenant.decrypted_api_key if hasattr(tenant, 'decrypted_api_key') else None
        
        # Initialize Gemini session with RAG
        gemini_session = GeminiLiveSession(
            tenant_id=str(tenant.id),
            company_name=tenant.company_name,
            api_key=api_key,
            db=db
        )
        await gemini_session.initialize()
        
        # Process query
        response_text = await gemini_session.process_text_query(data.query)
        
        # Save conversation
        conversation = Conversation(
            tenant_id=tenant.id,
            session_id=session_id,
            transcript=data.query,
            response=response_text,
            token_usage=0,
            duration=0.0
        )
        db.add(conversation)
        db.commit()
        
        return {"response": response_text, "session_id": session_id}
    except Exception as e:
        logger.error(f"[TEXT-QUERY] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge")
async def add_knowledge(knowledge: KnowledgeCreate, request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    
    entry = KnowledgeBase(
        tenant_id=tenant.id,
        category=knowledge.category,
        title=knowledge.title,
        content=knowledge.content
    )
    db.add(entry)
    db.commit()
    return {"status": "created"}

@app.get("/api/knowledge")
async def list_knowledge(request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == tenant.id).all()
    return [{"id": str(k.id), "category": k.category, "title": k.title, "content": k.content} for k in knowledge]

@app.get("/api/conversations")
async def get_conversations(request: Request, limit: int = 50, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    conversations = db.query(Conversation).filter(
        Conversation.tenant_id == tenant.id
    ).order_by(Conversation.created_at.desc()).limit(limit).all()
    return [{"transcript": c.transcript, "response": c.response, "created_at": c.created_at} for c in conversations]

@app.get("/api/introduction")
async def get_introduction(request: Request, db: Session = Depends(get_db)):
    """Return introduction audio using Google Cloud TTS with avatar voice"""
    from google_tts_service import GoogleTTSService
    from fastapi.responses import StreamingResponse
    import io
    import time
    
    logger.info(f"[INTRODUCTION] Request from {request.headers.get('Origin')}")
    
    tenant = await get_tenant_context(request, db)
    logger.info(f"[INTRODUCTION] Tenant: {tenant.company_name}")
    
    if not tenant.introduction_script:
        return JSONResponse(content={"text": ""})
    
    try:
        # Load avatar to get voice configuration
        avatar = None
        if tenant.avatar_id:
            avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
        
        if not avatar:
            logger.warning("[INTRODUCTION] No avatar found, returning text")
            return JSONResponse(content={"text": tenant.introduction_script})
        
        start_time = time.time()
        
        # Use avatar voice configuration
        voice_name = avatar.voice_name or "en-US-Neural2-F"
        gender = avatar.gender or "female"
        speaking_rate = tenant.speaking_rate or 1.0
        pitch = tenant.pitch or 0.0
        
        audio_content = await GoogleTTSService.generate_audio(
            tenant.introduction_script,
            voice_name,
            gender,
            speaking_rate,
            pitch
        )
        
        generation_time = time.time() - start_time
        logger.info(f"[INTRODUCTION] Generated in {generation_time:.2f}s with voice: {voice_name} ({gender})")
        
        if audio_content:
            return StreamingResponse(
                io.BytesIO(audio_content),
                media_type="audio/mpeg",
                headers={"X-Voice-Name": voice_name, "X-Avatar-Gender": gender}
            )
        else:
            logger.warning("[INTRODUCTION] TTS failed, returning text")
            return JSONResponse(content={"text": tenant.introduction_script})
            
    except Exception as e:
        logger.error(f"[INTRODUCTION] Error: {e}")
        return JSONResponse(content={"text": tenant.introduction_script})

@app.post("/api/voice-query")
async def voice_query(request: Request, db: Session = Depends(get_db)):
    """Process voice query: Browser STT → Gemini LLM → Google Cloud TTS with avatar voice"""
    from google_tts_service import GoogleTTSService
    from fastapi.responses import StreamingResponse
    import io
    import time
    
    logger.info(f"[VOICE-QUERY] Request from {request.headers.get('Origin')}")
    
    tenant = await get_tenant_context(request, db)
    logger.info(f"[VOICE-QUERY] Tenant: {tenant.company_name}")
    
    form = await request.form()
    transcript = form.get("transcript")
    session_id = form.get("session_id") or str(uuid.uuid4())
    
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcript provided")
    
    try:
        logger.info(f"[VOICE-QUERY] Transcript: {transcript}")
        
        api_key = tenant.decrypted_api_key if hasattr(tenant, 'decrypted_api_key') else None
        
        # Gemini LLM with RAG
        gemini_session = GeminiLiveSession(
            tenant_id=str(tenant.id),
            company_name=tenant.company_name,
            api_key=api_key,
            db=db
        )
        await gemini_session.initialize()
        
        response_text = await gemini_session.process_text_query(transcript)
        
        # Save conversation
        conversation = Conversation(
            tenant_id=tenant.id,
            session_id=session_id,
            transcript=transcript,
            response=response_text,
            token_usage=0,
            duration=0.0
        )
        db.add(conversation)
        db.commit()
        
        logger.info(f"[VOICE-QUERY] Gemini response: {response_text[:100]}...")
        
        # Load avatar to get voice configuration
        avatar = None
        if tenant.avatar_id:
            avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
        
        if not avatar:
            logger.warning("[VOICE-QUERY] No avatar found, returning text")
            return JSONResponse(content={"response": response_text, "session_id": session_id})
        
        # Generate audio using avatar voice configuration
        start_time = time.time()
        voice_name = avatar.voice_name or "en-US-Neural2-F"
        gender = avatar.gender or "female"
        speaking_rate = tenant.speaking_rate or 1.0
        pitch = tenant.pitch or 0.0
        
        audio_content = await GoogleTTSService.generate_audio(
            response_text,
            voice_name,
            gender,
            speaking_rate,
            pitch
        )
        
        generation_time = time.time() - start_time
        logger.info(f"[VOICE-QUERY] TTS generated in {generation_time:.2f}s with voice: {voice_name} ({gender})")
        
        if audio_content:
            return StreamingResponse(
                io.BytesIO(audio_content),
                media_type="audio/mpeg",
                headers={
                    "X-Session-ID": session_id,
                    "X-Voice-Name": voice_name,
                    "X-Avatar-Gender": gender
                }
            )
        else:
            logger.warning("[VOICE-QUERY] TTS failed, returning text")
            return JSONResponse(content={"response": response_text, "session_id": session_id})
        
    except Exception as e:
        logger.error(f"[VOICE-QUERY] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "3.0-gemini-multi-tenant"}

# WebSocket endpoint for real-time streaming (advanced)
@app.websocket("/ws/voice-stream")
async def voice_stream_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket for real-time audio streaming with Gemini Live API"""
    await websocket.accept()
    
    try:
        # Receive authentication
        auth_data = await websocket.receive_json()
        tenant_id = auth_data.get("tenant_id")
        signature = auth_data.get("signature")
        
        if not tenant_id or not signature:
            await websocket.close(code=1008, reason="Missing credentials")
            return
        
        # Verify tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant or tenant.widget_signature != signature:
            await websocket.close(code=1008, reason="Invalid credentials")
            return
        
        logger.info(f"[WS] Connected: {tenant.company_name}")
        
        # Get API key
        api_key = decrypt_api_key(tenant.gemini_api_key_encrypted) if tenant.gemini_api_key_encrypted else None
        
        # Initialize Gemini session
        gemini_session = GeminiLiveSession(
            tenant_id=str(tenant.id),
            company_name=tenant.company_name,
            api_key=api_key,
            db=db
        )
        await gemini_session.initialize()
        
        # Send ready signal
        await websocket.send_json({"status": "ready"})
        
        # Handle streaming messages
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "text_query":
                query = message.get("query")
                response = await gemini_session.process_text_query(query)
                
                await websocket.send_json({
                    "type": "response",
                    "text": response
                })
            
            elif message.get("type") == "close":
                break
    
    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    except Exception as e:
        logger.error(f"[WS] Error: {e}")
        await websocket.close(code=1011, reason=str(e))
