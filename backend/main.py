from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from database import init_db, get_db
from models import Tenant, Avatar, KnowledgeBase, Conversation
from tenant_middleware import get_tenant_context, encrypt_api_key, decrypt_api_key
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
    return [{"id": str(t.id), "company_name": t.company_name, "domain": t.domain, "status": t.status} for t in tenants]

@app.put("/admin/tenants/{tenant_id}/status")
def update_tenant_status(tenant_id: str, status: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.status = status
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0-multi-tenant"}
