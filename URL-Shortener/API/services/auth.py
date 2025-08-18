from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from API.config import settings
from API.exceptions import TokenExpired, TokenInvalid
from API.schemas import TokenPayload
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    refreshUrl="/api/v1/auth/refresh",
)

PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

OAUTH2_SCHEME_OPTIONAL = OAuth2PasswordBearer(    tokenUrl="/api/v1/auth/token",
    refreshUrl="/api/v1/auth/refresh", auto_error=False)

def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update(
        {
            "exp": expire.timestamp(),
            "issued_at": datetime.now(timezone.utc).timestamp(),
            "refresh_count": 0,
        }
    )
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def validate_token(
    token: str = Depends(OAUTH2_SCHEME),
) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        return TokenPayload.model_validate(payload)
    except jwt.ExpiredSignatureError:
        raise TokenExpired().to_http()
    except jwt.InvalidTokenError:
        raise TokenInvalid().to_http()




async def validate_token_optional(
    token: Optional[str] = Depends(OAUTH2_SCHEME_OPTIONAL),
) -> Optional[TokenPayload]:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        return TokenPayload.model_validate(payload)

    except jwt.ExpiredSignatureError:
        raise TokenExpired().to_http()
    except jwt.InvalidTokenError:
        raise TokenInvalid().to_http()

