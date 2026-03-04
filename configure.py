"""
Configuration Helper for Gemini Voice Agent
Validates environment and generates encryption keys
"""

import os
import sys
from cryptography.fernet import Fernet

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("[X] .env file not found")
        print("Creating from template...")
        
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("[OK] .env created from .env.example")
        else:
            print("[X] .env.example not found")
            return False
    else:
        print("[OK] .env file exists")
    
    return True

def check_gemini_key():
    """Check if Gemini API key is configured"""
    with open('.env', 'r') as f:
        content = f.read()
    
    # Extract the actual key value
    for line in content.split('\n'):
        if line.startswith('GEMINI_API_KEY='):
            key_value = line.split('=', 1)[1].strip()
            if key_value and key_value not in ['your-gemini-api-key-here', '']:
                print("[OK] GEMINI_API_KEY configured")
                return True
            else:
                print("[!] GEMINI_API_KEY not configured")
                print("    Get your key from: https://makersuite.google.com/app/apikey")
                return False
    
    print("[X] GEMINI_API_KEY not found in .env")
    return False

def check_encryption_key():
    """Check if encryption key is configured"""
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'ENCRYPTION_KEY=your-' in content or 'ENCRYPTION_KEY=' not in content:
        print("[!] ENCRYPTION_KEY not configured")
        print("    Generating new encryption key...")
        
        key = Fernet.generate_key().decode()
        
        # Update .env
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ENCRYPTION_KEY='):
                lines[i] = f'ENCRYPTION_KEY={key}'
                break
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"[OK] Generated ENCRYPTION_KEY: {key[:20]}...")
        return True
    else:
        print("[OK] ENCRYPTION_KEY configured")
        return True

def check_database_url():
    """Check if database URL is configured"""
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'DATABASE_URL=' in content:
        print("[OK] DATABASE_URL configured")
        return True
    else:
        print("[X] DATABASE_URL not found in .env")
        return False

def generate_widget_signature():
    """Generate a sample widget signature"""
    import hashlib
    import uuid
    
    signature = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    print(f"\nSample Widget Signature: {signature}")
    print("(This will be auto-generated when creating tenants)")

def print_summary():
    """Print configuration summary"""
    print("\n" + "="*60)
    print("Configuration Summary")
    print("="*60)
    
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                if 'KEY' in key or 'SECRET' in key:
                    # Mask sensitive values
                    if value and len(value) > 10:
                        masked = value[:10] + '...' + value[-4:]
                    else:
                        masked = '***'
                    print(f"  {key}: {masked}")
                else:
                    print(f"  {key}: {value}")

def main():
    print("="*60)
    print("Gemini Voice Agent - Configuration Helper")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check .env file
    if not check_env_file():
        all_ok = False
    
    print()
    
    # Check Gemini API key
    if not check_gemini_key():
        all_ok = False
    
    print()
    
    # Check encryption key
    if not check_encryption_key():
        pass  # Auto-generated
    
    print()
    
    # Check database URL
    if not check_database_url():
        all_ok = False
    
    print()
    
    # Generate sample widget signature
    generate_widget_signature()
    
    # Print summary
    print_summary()
    
    print("\n" + "="*60)
    if all_ok:
        print("[SUCCESS] Configuration is ready!")
        print("\nNext steps:")
        print("1. Run: docker-compose up -d")
        print("2. Open: http://localhost:3000 (Admin Dashboard)")
        print("3. Create your first tenant")
    else:
        print("[WARNING] Configuration incomplete")
        print("\nPlease:")
        print("1. Add GEMINI_API_KEY to .env")
        print("2. Get key from: https://makersuite.google.com/app/apikey")
        print("3. Run this script again to verify")
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
