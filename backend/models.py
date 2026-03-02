from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    avatar_id = Column(UUID(as_uuid=True))
    introduction_script = Column(Text)
    voice_model = Column(String(50), default="nova")
    openai_api_key_encrypted = Column(Text, nullable=False)
    status = Column(String(20), default="active")
    brand_colors = Column(JSON)
    widget_signature = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Avatar(Base):
    __tablename__ = "avatars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=False)
    default_voice = Column(String(50), default="nova")
    personality_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    transcript = Column(Text)
    response = Column(Text)
    token_usage = Column(Integer)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
