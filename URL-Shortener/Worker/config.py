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
