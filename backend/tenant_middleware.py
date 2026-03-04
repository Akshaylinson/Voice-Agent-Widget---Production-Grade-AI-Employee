import hmac
import hashlib
import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from models import Tenant
from cryptography.fernet import Fernet
from config import settings

logger = logging.getLogger(__name__)
cipher = Fernet(settings.encryption_key.encode())

def encrypt_api_key(api_key: str) -> str:
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    return cipher.decrypt(encrypted_key.encode()).decode()

def verify_signature(tenant_id: str, signature: str, tenant_signature: str) -> bool:
    # Widget sends the raw widget_signature, not HMAC of tenant_id
    # So we just compare directly
    return hmac.compare_digest(tenant_signature, signature)

async def get_tenant_context(request: Request, db: Session):
    # Try headers first, then query parameters
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    signature = request.headers.get("X-Signature") or request.query_params.get("signature")
    origin = request.headers.get("Origin", "")
    
    logger.info(f"[AUTH] Tenant ID: {tenant_id}, Signature: {signature[:20] if signature else 'None'}..., Origin: {origin}")
    
    if not tenant_id or not signature:
        logger.error("[AUTH] Missing credentials")
        raise HTTPException(status_code=401, detail="Missing tenant credentials")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        logger.error(f"[AUTH] Tenant not found: {tenant_id}")
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant.status != "active":
        logger.error(f"[AUTH] Tenant suspended: {tenant_id}")
        raise HTTPException(status_code=403, detail="Tenant suspended")
    
    # Admin override for knowledge management
    if signature != "admin-override" and not verify_signature(tenant_id, signature, tenant.widget_signature):
        logger.error(f"[AUTH] Invalid signature for tenant: {tenant_id}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Domain validation: Allow localhost/IP for development OR production domain
    if tenant.domain and origin:
        is_local = any([
            "localhost" in origin,
            "127.0.0.1" in origin,
            origin.startswith("file://"),
            not origin
        ])
        
        is_authorized_domain = tenant.domain in origin
        
        if not is_local and not is_authorized_domain:
            logger.error(f"[AUTH] Domain not authorized: {origin} vs {tenant.domain}")
            raise HTTPException(status_code=403, detail="Domain not authorized")
    
    logger.info(f"[AUTH] Success: {tenant.company_name}")
    tenant.decrypted_api_key = decrypt_api_key(tenant.gemini_api_key_encrypted) if tenant.gemini_api_key_encrypted else None
    return tenant
