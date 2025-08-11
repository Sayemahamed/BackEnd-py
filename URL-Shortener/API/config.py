from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

"""
This module contains the configuration settings for the API, loaded from environment
variables or a .env file.
"""


class Settings(BaseSettings):
    """API Configuration Settings"""

    # --- Core ---
    SECRET_KEY: str = Field(..., description="Secret key for signing JWTs")
    ALGORITHM: str = Field("HS256", description="Algorithm used for JWT signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        90, description="Access token validity duration in minutes"
    )

    # --- Database ---
    # Example: postgresql+asyncpg://user:password@host:port/dbname
    POSTGRES_URL_ASYNC: str = Field(..., description="Async PostgreSQL connection URL")
    POOL_SIZE: int = Field(
        10, description="Number of connections to keep open in the pool"
    )
    MAX_OVERFLOW: int = Field(
        20, description="Maximum number of connections allowed beyond pool_size"
    )
    POOL_TIMEOUT: int = Field(
        30, description="Timeout in seconds for acquiring a connection from the pool"
    )
    POOL_RECYCLE: int = Field(
        1800,
        description="Recycle connections after this many seconds (e.g., 30 minutes)",
    )

    # --- Services / External APIs ---
    REDIS_URL: str = Field(..., description="Redis connection URL")

    model_config = SettingsConfigDict(
        env_file=".env",  # Load .env file
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields found in the environment
        case_sensitive=False,  # Environment variable names are case-insensitive
    )


# Create a single instance of settings to be imported elsewhere
settings = Settings()  # type:ignore