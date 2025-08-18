from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class TokenPayload(BaseModel):
    user_id: str
    scopes: List[str] = []
    issued_at: datetime
    refresh_count: int
    exp: datetime


class TokenResponse(BaseModel):
    """Schema for the response containing the access token."""

    access_token: str
    token_type: str

    # Pydantic V2 configuration
    model_config = ConfigDict(from_attributes=True)
