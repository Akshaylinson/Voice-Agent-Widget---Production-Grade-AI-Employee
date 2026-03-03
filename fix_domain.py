import sys
sys.path.append('backend')

from database import SessionLocal
from models import Tenant

db = SessionLocal()

# Find the Codeless AI tenant
tenant_id = 'e78f6bbe-4cf0-471c-82cc-20f29a08506f'
tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

if tenant:
    print(f"Current domain: {tenant.domain}")
    print(f"Company: {tenant.company_name}")
    
    # Update to localhost
    tenant.domain = 'localhost'
    db.commit()
    print(f"✅ Updated domain to: localhost")
else:
    print(f"❌ Tenant not found: {tenant_id}")

db.close()
