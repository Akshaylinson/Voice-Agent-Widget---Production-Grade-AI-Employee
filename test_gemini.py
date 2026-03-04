"""
Test script for Gemini Voice Agent
Run: python test_gemini.py
"""

import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Add backend to path
sys.path.insert(0, 'backend')

from models import Base, Tenant, KnowledgeBase
from gemini_service import (
    GeminiLiveSession,
    generate_embedding,
    retrieve_knowledge_rag,
    generate_knowledge_embedding
)
from tenant_middleware import encrypt_api_key

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/voice_agent_multi_tenant")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set in environment")
    sys.exit(1)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_embedding_generation():
    """Test 1: Embedding Generation"""
    print("\n🧪 Test 1: Embedding Generation")
    print("-" * 50)
    
    try:
        text = "We offer web development services using React and Node.js"
        embedding = await generate_embedding(text, GEMINI_API_KEY)
        
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        print(f"   Sample values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

async def test_knowledge_retrieval():
    """Test 2: RAG Knowledge Retrieval"""
    print("\n🧪 Test 2: RAG Knowledge Retrieval")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        # Create test tenant
        tenant = Tenant(
            company_name="Test Corp",
            domain="test.com",
            gemini_api_key_encrypted=encrypt_api_key(GEMINI_API_KEY),
            widget_signature="test123"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        print(f"✅ Created test tenant: {tenant.id}")
        
        # Add test knowledge
        knowledge_entries = [
            {
                "category": "services",
                "title": "Web Development",
                "content": "We build modern web applications using React, Vue, and Angular"
            },
            {
                "category": "services",
                "title": "Mobile Development",
                "content": "We create iOS and Android apps using React Native and Flutter"
            },
            {
                "category": "pricing",
                "title": "Pricing Plans",
                "content": "Our plans start at $99/month for basic and $299/month for premium"
            }
        ]
        
        for entry_data in knowledge_entries:
            entry = KnowledgeBase(
                tenant_id=tenant.id,
                **entry_data
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            
            # Generate embedding
            await generate_knowledge_embedding(db, str(entry.id), GEMINI_API_KEY)
            print(f"✅ Added knowledge: {entry.title}")
        
        # Test retrieval
        query = "What mobile services do you offer?"
        context = await retrieve_knowledge_rag(
            db,
            str(tenant.id),
            query,
            GEMINI_API_KEY,
            top_k=2
        )
        
        print(f"\n📝 Query: {query}")
        print(f"📚 Retrieved context:\n{context[:200]}...")
        
        # Cleanup
        db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == tenant.id).delete()
        db.query(Tenant).filter(Tenant.id == tenant.id).delete()
        db.commit()
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def test_gemini_session():
    """Test 3: Gemini Live Session"""
    print("\n🧪 Test 3: Gemini Live Session")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        # Create test tenant with knowledge
        tenant = Tenant(
            company_name="Acme Corp",
            domain="acme.com",
            gemini_api_key_encrypted=encrypt_api_key(GEMINI_API_KEY),
            widget_signature="test456"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Add knowledge
        knowledge = KnowledgeBase(
            tenant_id=tenant.id,
            category="company",
            title="About Us",
            content="Acme Corp is a leading technology company specializing in AI solutions. We help businesses automate customer service with voice agents."
        )
        db.add(knowledge)
        db.commit()
        
        print(f"✅ Created test tenant: {tenant.company_name}")
        
        # Initialize Gemini session
        session = GeminiLiveSession(
            tenant_id=str(tenant.id),
            company_name=tenant.company_name,
            api_key=GEMINI_API_KEY,
            db=db
        )
        await session.initialize()
        
        print("✅ Gemini session initialized")
        
        # Test query
        query = "What does your company do?"
        response = await session.process_text_query(query)
        
        print(f"\n💬 Query: {query}")
        print(f"🤖 Response: {response}")
        
        # Cleanup
        db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == tenant.id).delete()
        db.query(Tenant).filter(Tenant.id == tenant.id).delete()
        db.commit()
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("🚀 Gemini Voice Agent Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1
    results.append(await test_embedding_generation())
    
    # Test 2
    results.append(await test_knowledge_retrieval())
    
    # Test 3
    results.append(await test_gemini_session())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
