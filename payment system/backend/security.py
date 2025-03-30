import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "fallback_secret_should_be_changed_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Security context configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Use bcrypt for modern password hashing
    deprecated="auto",
    bcrypt__rounds=12  # Adjusted for security vs performance balance
)

class TokenData(BaseModel):
    """Token payload validation model"""
    username: str
    role: str
    user_id: int
    branch_id: Optional[int] = None

def hash_password(password: str) -> str:
    """Secure password hashing with bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safe password verification with constant-time comparison"""
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT with security best practices"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Standard claims for security
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "payment-system",
        "aud": "payment-system-users"
    })
    
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
        headers={"kid": "v1"}  # Key rotation identifier
    )

def decode_jwt_token(token: str) -> TokenData:
    """Secure token decoding with full validation"""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="payment-system-users",
            issuer="payment-system"
        )
        
        # Manual claim validation
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise JWTError("Token expired")
            
        return TokenData(
            username=payload["sub"],
            role=payload["role"],
            user_id=payload["uid"],
            branch_id=payload.get("bid")
        )
        
    except JWTError as e:
        # Security: Generic error messages to prevent information leakage
        raise ValueError("Invalid authentication credentials") from e