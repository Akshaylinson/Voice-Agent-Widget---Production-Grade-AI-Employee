from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

from database import init_db, get_db
from models import Tenant, Avatar, KnowledgeBase, Conversation
from tenant_middleware import get_tenant_context, encrypt_api_key, decrypt_api_key
from openai_service import transcribe_audio, generate_response, text_to_speech
import hmac
import hashlib

app = FastAPI(title="Multi-Tenant Voice Agent API")

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
    openai_api_key: str
    avatar_id: Optional[str] = None
    introduction_script: Optional[str] = None
    voice_model: str = "nova"

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
        openai_api_key_encrypted=encrypt_api_key(tenant_data.openai_api_key),
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
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    avatar = None
    if tenant.avatar_id:
        avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
    
    # Get analytics
    total_conversations = db.query(Conversation).filter(Conversation.tenant_id == tenant.id).count()
    total_tokens = db.query(func.sum(Conversation.token_usage)).filter(Conversation.tenant_id == tenant.id).scalar() or 0
    last_activity = db.query(Conversation).filter(Conversation.tenant_id == tenant.id).order_by(
        Conversation.created_at.desc()
    ).first()
    
    return {
        "id": str(tenant.id),
        "company_name": tenant.company_name,
        "domain": tenant.domain,
        "avatar_id": str(tenant.avatar_id) if tenant.avatar_id else None,
        "avatar_url": avatar.image_url if avatar else None,
        "introduction_script": tenant.introduction_script,
        "voice_model": tenant.voice_model,
        "voice_tone": tenant.voice_tone,
        "temperature": tenant.temperature,
        "max_tokens": tenant.max_tokens,
        "status": tenant.status,
        "brand_colors": tenant.brand_colors,
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
    voice_model: Optional[str] = None
    voice_tone: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    openai_api_key: Optional[str] = None
    brand_colors: Optional[dict] = None

@app.put("/admin/tenant/{tenant_id}")
def update_tenant(tenant_id: str, data: TenantUpdate, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if data.company_name: tenant.company_name = data.company_name
    if data.domain: tenant.domain = data.domain
    if data.avatar_id: tenant.avatar_id = data.avatar_id
    if data.introduction_script is not None: tenant.introduction_script = data.introduction_script
    if data.voice_model: tenant.voice_model = data.voice_model
    if data.voice_tone: tenant.voice_tone = data.voice_tone
    if data.temperature is not None: tenant.temperature = data.temperature
    if data.max_tokens: tenant.max_tokens = data.max_tokens
    if data.openai_api_key: tenant.openai_api_key_encrypted = encrypt_api_key(data.openai_api_key)
    if data.brand_colors: tenant.brand_colors = data.brand_colors
    
    db.commit()
    return {"status": "updated"}

@app.get("/admin/tenant/{tenant_id}/knowledge")
def get_tenant_knowledge(tenant_id: str, db: Session = Depends(get_db)):
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == tenant_id).all()
    return [{"id": str(k.id), "category": k.category, "title": k.title, "content": k.content, "is_active": k.is_active} for k in knowledge]

@app.post("/admin/tenant/{tenant_id}/knowledge")
def create_tenant_knowledge(tenant_id: str, knowledge: KnowledgeCreate, db: Session = Depends(get_db)):
    entry = KnowledgeBase(
        tenant_id=tenant_id,
        category=knowledge.category,
        title=knowledge.title,
        content=knowledge.content
    )
    db.add(entry)
    db.commit()
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
def create_avatar(name: str, image_url: str, default_voice: str = "nova", db: Session = Depends(get_db)):
    avatar = Avatar(name=name, image_url=image_url, default_voice=default_voice)
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    return {"id": str(avatar.id), "name": avatar.name}

@app.get("/admin/avatars")
def list_avatars(db: Session = Depends(get_db)):
    avatars = db.query(Avatar).all()
    return [{"id": str(a.id), "name": a.name, "image_url": a.image_url} for a in avatars]

# Tenant-Aware Public Endpoints
@app.get("/api/config")
async def get_config(request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    
    avatar = None
    if tenant.avatar_id:
        avatar = db.query(Avatar).filter(Avatar.id == tenant.avatar_id).first()
    
    return {
        "company_name": tenant.company_name,
        "avatar_url": avatar.image_url if avatar else None,
        "introduction_script": tenant.introduction_script,
        "voice_model": tenant.voice_model,
        "brand_colors": tenant.brand_colors
    }

@app.post("/api/text-query")
async def process_text_query(data: TextQuery, request: Request, db: Session = Depends(get_db)):
    tenant = await get_tenant_context(request, db)
    session_id = data.session_id or str(uuid.uuid4())
    
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.tenant_id == tenant.id,
        KnowledgeBase.is_active == True
    ).all()
    
    knowledge_context = "\n".join([f"{k.title}: {k.content}" for k in knowledge])
    
    # Use tenant's OpenAI API key
    # response_text = await generate_response(data.query, knowledge_context, tenant.company_name, tenant.decrypted_api_key)
    response_text = f"Response from {tenant.company_name} based on knowledge base."
    
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
    logger.info(f"[INTRODUCTION] Request from {request.headers.get('Origin')}")
    
    tenant = await get_tenant_context(request, db)
    logger.info(f"[INTRODUCTION] Tenant resolved: {tenant.company_name}")
    
    # Generate introduction audio
    if tenant.introduction_script:
        try:
            audio_bytes = await text_to_speech(
                tenant.introduction_script,
                tenant.voice_model or "nova",
                tenant.decrypted_api_key
            )
            from fastapi.responses import Response
            return Response(content=audio_bytes, media_type="audio/mpeg")
        except Exception as e:
            logger.error(f"[INTRODUCTION] TTS failed: {e}")
    
    # Return empty if no script or TTS fails
    from fastapi.responses import Response
    return Response(content=b"", media_type="audio/mpeg")

@app.post("/api/voice-query")
async def voice_query(request: Request, db: Session = Depends(get_db)):
    logger.info(f"[VOICE-QUERY] Request from {request.headers.get('Origin')}")
    
    tenant = await get_tenant_context(request, db)
    logger.info(f"[VOICE-QUERY] Tenant resolved: {tenant.company_name}")
    
    # Parse form data
    form = await request.form()
    audio_file = form.get("audio")
    session_id = form.get("session_id") or str(uuid.uuid4())
    
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    try:
        # Read audio bytes
        audio_bytes = await audio_file.read()
        logger.info(f"[VOICE-QUERY] Audio size: {len(audio_bytes)} bytes")
        
        # Step 1: Transcribe audio (Whisper)
        transcript = await transcribe_audio(audio_bytes, tenant.decrypted_api_key)
        
        # Step 2: Get knowledge base
        knowledge = db.query(KnowledgeBase).filter(
            KnowledgeBase.tenant_id == tenant.id,
            KnowledgeBase.is_active == True
        ).all()
        knowledge_context = "\n".join([f"{k.title}: {k.content}" for k in knowledge])
        
        # Step 3: Generate response (GPT-4)
        response_text = await generate_response(
            transcript,
            knowledge_context,
            tenant.company_name,
            tenant.decrypted_api_key
        )
        
        # Step 4: Convert to speech (TTS)
        response_audio = await text_to_speech(
            response_text,
            tenant.voice_model or "nova",
            tenant.decrypted_api_key
        )
        
        # Step 5: Save conversation
        conversation = Conversation(
            tenant_id=tenant.id,
            session_id=session_id,
            transcript=transcript,
            response=response_text,
            token_usage=0,  # TODO: track actual tokens
            duration=0.0
        )
        db.add(conversation)
        db.commit()
        
        logger.info(f"[VOICE-QUERY] Success: {response_text[:100]}...")
        
        from fastapi.responses import Response
        return Response(
            content=response_audio,
            media_type="audio/mpeg",
            headers={"X-Session-ID": session_id}
        )
        
    except Exception as e:
        logger.error(f"[VOICE-QUERY] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0-multi-tenant"}
