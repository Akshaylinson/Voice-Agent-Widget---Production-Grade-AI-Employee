import logging
import os
import json
import asyncio
import base64
from typing import Optional, List, Dict
import google.generativeai as genai
from sqlalchemy.orm import Session
from models import KnowledgeBase

logger = logging.getLogger(__name__)

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
GEMINI_LIVE_MODEL = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.0-flash-exp")

class GeminiLiveSession:
    """Manages Gemini Live API streaming session"""
    
    def __init__(self, tenant_id: str, company_name: str, api_key: str, db: Session):
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.api_key = api_key or GEMINI_API_KEY
        self.db = db
        self.model = None
        self.chat = None
        
        genai.configure(api_key=self.api_key)
    
    async def initialize(self):
        """Initialize Gemini model with RAG context"""
        try:
            # Retrieve knowledge context
            knowledge_context = await self._get_knowledge_context()
            
            # Build system instruction
            system_instruction = f"""You are an AI employee of {self.company_name}.

CRITICAL RULES:
- Answer ONLY using the provided company knowledge below
- If information is not in the knowledge base, say "I don't have that information"
- Be concise, friendly, and professional
- Keep responses under 100 words

COMPANY KNOWLEDGE:
{knowledge_context}"""
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=GEMINI_LIVE_MODEL,
                system_instruction=system_instruction
            )
            
            self.chat = self.model.start_chat(history=[])
            logger.info(f"[GEMINI] Session initialized for {self.company_name}")
            
        except Exception as e:
            logger.error(f"[GEMINI] Initialization failed: {e}")
            raise
    
    async def _get_knowledge_context(self) -> str:
        """Retrieve all active knowledge for tenant"""
        try:
            knowledge = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.tenant_id == self.tenant_id,
                KnowledgeBase.is_active == True
            ).all()
            
            if not knowledge:
                return "No specific company knowledge available."
            
            context = "\n\n".join([
                f"Category: {k.category}\nTitle: {k.title}\nContent: {k.content}"
                for k in knowledge
            ])
            
            logger.info(f"[GEMINI] Loaded {len(knowledge)} knowledge entries")
            return context
            
        except Exception as e:
            logger.error(f"[GEMINI] Knowledge retrieval failed: {e}")
            return "Knowledge retrieval error."
    
    async def process_text_query(self, query: str) -> str:
        """Process text query with RAG grounding"""
        try:
            logger.info(f"[GEMINI] Processing query: {query[:100]}...")
            
            # Generate response
            response = await asyncio.to_thread(
                self.chat.send_message,
                query
            )
            
            answer = response.text
            logger.info(f"[GEMINI] Response: {answer[:100]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"[GEMINI] Query processing failed: {e}")
            raise

async def generate_embedding(text: str, api_key: Optional[str] = None) -> List[float]:
    """Generate embedding for RAG retrieval"""
    try:
        genai.configure(api_key=api_key or GEMINI_API_KEY)
        
        result = await asyncio.to_thread(
            genai.embed_content,
            model=f"models/{GEMINI_EMBEDDING_MODEL}",
            content=text,
            task_type="retrieval_query"
        )
        
        embedding = result['embedding']
        logger.info(f"[GEMINI] Generated embedding: {len(embedding)} dimensions")
        
        return embedding
        
    except Exception as e:
        logger.error(f"[GEMINI] Embedding generation failed: {e}")
        raise

async def retrieve_knowledge_rag(
    db: Session,
    tenant_id: str,
    query: str,
    api_key: Optional[str] = None,
    top_k: int = 5
) -> str:
    """RAG knowledge retrieval using pgvector similarity search"""
    try:
        # Generate query embedding
        query_embedding = await generate_embedding(query, api_key)
        
        # Vector similarity search
        knowledge = db.query(KnowledgeBase).filter(
            KnowledgeBase.tenant_id == tenant_id,
            KnowledgeBase.is_active == True,
            KnowledgeBase.embedding.isnot(None)
        ).order_by(
            KnowledgeBase.embedding.cosine_distance(query_embedding)
        ).limit(top_k).all()
        
        if not knowledge:
            # Fallback to all knowledge
            knowledge = db.query(KnowledgeBase).filter(
                KnowledgeBase.tenant_id == tenant_id,
                KnowledgeBase.is_active == True
            ).all()
        
        context = "\n\n".join([
            f"{k.title}: {k.content}"
            for k in knowledge
        ])
        
        logger.info(f"[RAG] Retrieved {len(knowledge)} relevant entries")
        return context
        
    except Exception as e:
        logger.error(f"[RAG] Retrieval failed: {e}")
        # Fallback to simple retrieval
        knowledge = db.query(KnowledgeBase).filter(
            KnowledgeBase.tenant_id == tenant_id,
            KnowledgeBase.is_active == True
        ).all()
        return "\n\n".join([f"{k.title}: {k.content}" for k in knowledge])

async def generate_knowledge_embedding(
    db: Session,
    knowledge_id: str,
    api_key: Optional[str] = None
):
    """Generate and store embedding for knowledge entry"""
    try:
        knowledge = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_id
        ).first()
        
        if not knowledge:
            return
        
        # Generate embedding
        text = f"{knowledge.title} {knowledge.content}"
        embedding = await generate_embedding(text, api_key)
        
        # Store embedding
        knowledge.embedding = embedding
        db.commit()
        
        logger.info(f"[GEMINI] Embedding stored for knowledge: {knowledge.title}")
        
    except Exception as e:
        logger.error(f"[GEMINI] Embedding storage failed: {e}")
        db.rollback()

async def text_to_speech_gemini(text: str, voice: str = "Puck") -> bytes:
    """Generate speech using Gemini (placeholder - Gemini doesn't have native TTS yet)"""
    # Note: Gemini doesn't have TTS API yet, using text response for now
    # In production, integrate with Google Cloud TTS or keep browser TTS
    logger.warning("[GEMINI] TTS not available, returning empty audio")
    return b""
