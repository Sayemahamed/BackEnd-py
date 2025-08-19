import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import TEXT, UUID
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            server_default=text("uuidv7()"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )

    username: str = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            comment="Alphanumeric or underscores, 3–50 chars",
        ),
        min_length=3,
        max_length=50,
        regex=r"^[A-Za-z0-9_]+$",
    )

    email: EmailStr = Field(
        sa_column=Column(
            TEXT,
            nullable=False,
            index=True,
            unique=True,
            comment="Case-insensitive email",
        ),
        max_length=254,
    )

    hashed_password: str = Field(
        sa_column=Column(
            TEXT,
            nullable=False,
            comment="Stores bcrypt/Argon2 hashes",
        )
    )

    jwt_expires: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="JWT expiration timestamp",
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="Record creation timestamp",
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
            comment="Last update timestamp",
        )
    )


class ShortURL(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            server_default=text("uuidv7()"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )

    original_url: str = Field(
        sa_column=Column(
            TEXT,
            nullable=False,
            comment="Original URL to redirect to",
        )
    )

    short_code: str = Field(
        sa_column=Column(
            String(12),
            nullable=False,
            unique=True,
            index=True,
            comment="Generated slug (e.g. aB78xZ)",
        ),
    )

    user_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
            nullable=True,
            index=True,
            comment="FK to User.id, nullable for anonymous links",
        ),
    )

    visit_count: int = Field(
        default=0,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=text("0"),
            comment="Number of times the short URL was visited",
        ),
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="Record creation timestamp",
        )
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
            comment="Optional expiration timestamp",
        ),
    )


class Visit(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            server_default=text("uuidv7()"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )

    short_url_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shorturl.id"),
            nullable=False,
            index=True,
            comment="FK to ShortURL.id",
        )
    )

    visited_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="Timestamp of the visit",
        )
    )

    ip_address: str = Field(
        sa_column=Column(
            String(45),
            nullable=False,
            comment="Visitor IP address (v4 or v6)",
        )
    )

    user_agent: str = Field(
        sa_column=Column(
            TEXT,
            nullable=False,
            comment="User-Agent header text",
        )
    )
