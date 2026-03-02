import hmac
import hashlib
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from models import Tenant
from cryptography.fernet import Fernet
from config import settings

cipher = Fernet(settings.encryption_key.encode())

def encrypt_api_key(api_key: str) -> str:
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    return cipher.decrypt(encrypted_key.encode()).decode()

def verify_signature(tenant_id: str, signature: str, tenant_signature: str) -> bool:
    expected = hmac.new(
        tenant_signature.encode(),
        tenant_id.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

async def get_tenant_context(request: Request, db: Session):
    tenant_id = request.headers.get("X-Tenant-ID")
    signature = request.headers.get("X-Signature")
    
    if not tenant_id or not signature:
        raise HTTPException(status_code=401, detail="Missing tenant credentials")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant.status != "active":
        raise HTTPException(status_code=403, detail="Tenant suspended")
    
    if not verify_signature(tenant_id, signature, tenant.widget_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    origin = request.headers.get("Origin", "")
    if tenant.domain and tenant.domain not in origin:
        raise HTTPException(status_code=403, detail="Domain not authorized")
    
    tenant.decrypted_api_key = decrypt_api_key(tenant.openai_api_key_encrypted)
    return tenant
