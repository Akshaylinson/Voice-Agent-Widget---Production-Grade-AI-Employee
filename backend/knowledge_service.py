from sqlalchemy.orm import Session
from models import CompanyKnowledge
from typing import List

def retrieve_knowledge(db: Session, client_id: str, query: str) -> str:
    """Retrieve relevant knowledge from client's database"""
    knowledge_entries = db.query(CompanyKnowledge).filter(
        CompanyKnowledge.client_id == client_id,
        CompanyKnowledge.is_active == True
    ).all()
    
    if not knowledge_entries:
        return "No company knowledge available."
    
    context = "\n\n".join([
        f"Category: {entry.category}\nTitle: {entry.title}\nContent: {entry.content}"
        for entry in knowledge_entries
    ])
    
    return context

def add_knowledge(db: Session, client_id: str, category: str, title: str, content: str, meta_data: dict = None):
    """Add new knowledge entry"""
    knowledge = CompanyKnowledge(
        client_id=client_id,
        category=category,
        title=title,
        content=content,
        meta_data=meta_data
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge

def get_all_knowledge(db: Session, client_id: str) -> List[CompanyKnowledge]:
    """Get all knowledge entries for a client"""
    return db.query(CompanyKnowledge).filter(
        CompanyKnowledge.client_id == client_id
    ).all()
