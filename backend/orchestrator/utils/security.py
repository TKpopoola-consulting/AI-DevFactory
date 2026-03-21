"""
Security utilities for authentication
"""
import jwt
import time
from typing import Optional
from pydantic import BaseModel

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenData(BaseModel):
    user_id: str
    roles: list = []


def create_access_token(user_id: str, roles: list = None) -> str:
    """Create JWT access token"""
    payload = {
        "sub": user_id,
        "roles": roles or [],
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload.get("sub", "anonymous"),
            roles=payload.get("roles", [])
        )
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def require_role(role: str):
    """Decorator to require a specific role"""
    def decorator(token_data: TokenData):
        if role not in token_data.roles:
            raise Exception(f"Role {role} required")
        return token_data
    return decorator


class DataEncryptor:
    """Simple encryptor for sensitive data"""
    def __init__(self):
        self.key = "simple-encryption-key-change-in-production"
    
    def encrypt(self, data: str) -> bytes:
        """Simple encryption (in production, use proper encryption)"""
        return data.encode()
    
    def decrypt(self, data: bytes) -> str:
        """Simple decryption"""
        return data.decode()
