from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from API.config import settings
from API.exceptions import TokenExpired, TokenInvalid
from API.schemas import TokenPayload

# OAuth2 scheme for token authentication
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=False
)

def _create_token(
    data: Dict[str, Any], 
    expires_delta: timedelta, 
    token_type: str = "access"
) -> str:
    """Create a JWT token with the given data and expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": token_type,
        "jti": str(uuid4())  # Unique identifier for token
    })
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_access_token(data: Dict[str, Any]) -> str:
    """Create an access token with short expiration."""
    return _create_token(
        data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token with long expiration."""
    return _create_token(
        data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )

async def get_current_user(
    token: Optional[str] = Depends(OAUTH2_SCHEME)
) -> TokenPayload:
    """Dependency to get current user from token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        
        # Additional validation for token type
        if payload.get("type") != "access":
            raise TokenInvalid(detail="Invalid token type")
            
        return TokenPayload.model_validate(payload)
        
    except jwt.ExpiredSignatureError:
        raise TokenExpired().to_http()
    except (jwt.InvalidTokenError, jwt.PyJWTError) as e:
        raise TokenInvalid(detail=str(e)).to_http()

def validate_refresh_token(token: str) -> TokenPayload:
    """Validate a refresh token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        
        if payload.get("type") != "refresh":
            raise TokenInvalid(detail="Invalid refresh token")
            
        return TokenPayload.model_validate(payload)
        
    except jwt.ExpiredSignatureError:
        raise TokenExpired(detail="Refresh token has expired").to_http()
    except (jwt.InvalidTokenError, jwt.PyJWTError) as e:
        raise TokenInvalid(detail=str(e)).to_http()
