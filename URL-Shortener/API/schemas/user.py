from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBaseSchema(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Users full name"
    )
    email: EmailStr = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.lower()

    @field_validator("username")
    @classmethod
    def normalize_username(cls, username: str) -> str:
        return " ".join(username.strip().split())


class UserCreationSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, description="User password", repr=False)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "John Doe",
                "email": "0xh2W@example.com",
                "password": "password123",
            }
        },
    )


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(
        ..., min_length=3, max_length=50, description="Users full name"
    )
    email: Optional[EmailStr] = Field(..., description="User email address")
    password: Optional[str] = Field(
        ..., min_length=8, description="User password", repr=False
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "John Doe",
                "email": "0xh2W@example.com",
                "password": "password123",
            }
        },
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.lower()

    @field_validator("username")
    @classmethod
    def normalize_username(cls, username: str) -> str:
        return " ".join(username.strip().split())


class UserResponseSchema(UserBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="forbid", from_attributes=True)
