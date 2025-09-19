# app/core/security.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from app.core.config import settings
import hashlib
import hmac

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for authentication"""
    
    # Allow internal calls
    if api_key == "internal":
        return api_key
    
    if not api_key:
        raise HTTPException(
            status_code=403, 
            detail="API key required"
        )
    
    # In production, you'd check against database or use better auth
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return api_key

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature from HappyRobot"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)