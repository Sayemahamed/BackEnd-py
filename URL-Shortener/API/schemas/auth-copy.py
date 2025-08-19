from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TokenPayload(BaseModel):
    """Payload for JWT tokens"""
    user_id: str
    scopes: List[str] = []
    issued_at: datetime
    exp: datetime
    type: str = "access"


class TokenBase(BaseModel):
    """Base model for token responses"""
    access_token: str
    refresh_token: str
    token_type: str


class TokenResponse(TokenBase):
    """Response model for token generation"""
    pass


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


class TokenRefreshResponse(TokenBase):
    """Response model for token refresh"""
    pass


# Pydantic V2 configuration for all models
for model in [TokenPayload, TokenResponse, TokenRefreshRequest, TokenRefreshResponse]:
    model.model_config = ConfigDict(from_attributes=True)
