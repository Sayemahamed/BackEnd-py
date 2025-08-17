import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, String, text
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
