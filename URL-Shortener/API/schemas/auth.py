from datetime import datetime
from typing import List

from pydantic import BaseModel


class TokenPayload(BaseModel):
    user_id: str
    scopes: List[str] = []
    issued_at: datetime
    refresh_count: int
    exp: datetime
