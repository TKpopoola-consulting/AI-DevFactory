import jwt
import time
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from cryptography.fernet import Fernet
from .error_handler import log_error

# Configuration (should be in environment variables)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENCRYPTION_KEY = Fernet.generate_key()  # In prod, load from secrets manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    user_id: str
    roles: list

def create_access_token(user_id: str, roles: list) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(user_id=payload["sub"], roles=payload["roles"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def require_role(role: str):
    def decorator(token_data: TokenData = Depends(verify_token)):
        if role not in token_data.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return token_data
    return decorator

class DataEncryptor:
    def __init__(self, key: bytes = ENCRYPTION_KEY):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, token: bytes) -> str:
        return self.cipher.decrypt(token).decode()