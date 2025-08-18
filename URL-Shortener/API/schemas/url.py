from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class URLCreationSchema(BaseModel):
    original_url: HttpUrl = Field(
        ...,
        description="The URL to shorten (must start with http:// or https://)",
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="Optional expiration timestamp (must be in the future)",
    )

    # Forbid extra fields and allow population from attribute names
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    @field_validator("expires_at")
    def check_expires_in_future(cls, v: datetime) -> datetime:
        if v <= datetime.utcnow():
            raise ValueError("expires_at must be a future datetime")
        return v


class URLCreatedResponseSchema(BaseModel):
    id: UUID = Field(..., description="Primary key of the ShortURL record")
    short_code: str = Field(..., description="Generated slug (e.g. aB78xZ)")
    original_url: HttpUrl = Field(..., description="The original URL that was shortened")
    short_url: HttpUrl = Field(..., description="Full shortened URL (including domain)")
    created_at: datetime = Field(..., description="When this short link was created")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp, if any")

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )


class URLInfo(BaseModel):
    id: UUID = Field(..., description="Short URL entry ID")
    short_url: HttpUrl = Field(..., description="Full shortened URL")
    original_url: HttpUrl = Field(..., description="Original target URL")
    visit_count: int = Field(
        ...,
        ge=0,
        description="Total number of times this URL was visited",
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp, if set")

    model_config = ConfigDict(extra="forbid")


class URLsSchema(BaseModel):
    urls: List[URLInfo] = Field(..., description="List of shortened URLs")

    model_config = ConfigDict(extra="forbid")
