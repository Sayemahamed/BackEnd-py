from typing import Optional

from API.db import get_async_session
from API.exceptions import IntegrityError, UserNotFound
from API.schemas import (
    TokenPayload,
    URLCreatedResponseSchema,
    URLCreationSchema,
    URLInfo,
    URLsSchema,
)
from API.services import (
    URLServices,
    UserService,
    validate_token,
    validate_token_optional,
)
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

url_router = APIRouter()


@url_router.post("/", response_model=URLCreatedResponseSchema, description="")
async def shorten_url(
    url_data: URLCreationSchema,
    url_service: URLServices = Depends(),
    user_service: UserService = Depends(),
    token: Optional[TokenPayload] = Depends(validate_token_optional),
    session: AsyncSession = Depends(get_async_session),
) -> URLCreatedResponseSchema:
    user = None
    if token is not None:
        user = await user_service.get_user_by_id(token.user_id, session)
        if not user:
            raise UserNotFound().to_http()
    try:
        url = await url_service.create_url(url_data, user, session)
        return URLCreatedResponseSchema(
            id=url.id,
            short_code=str(url.short_code),
            original_url=url.original_url,
            short_url=str(url.short_code),
            created_at=url.created_at,
            expires_at=url.expires_at,
        )
    except IntegrityError as exp:
        raise exp.to_http()


@url_router.get(
    "/all",
    response_model=URLsSchema,
    description="List of shortened URLs created by the user",
)
async def get_urls(
    token: TokenPayload = Depends(validate_token),
    url_service: URLServices = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> URLsSchema:
    user = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise UserNotFound().to_http()
    urls = await url_service.get_urls(user, session)
    return URLsSchema(
        urls=[
            URLInfo(
                id=url.id,
                original_url=url.original_url,
                short_url=str(url.short_code),
                visit_count=url.visit_count,
                created_at=url.created_at,
                expires_at=url.expires_at,
            )
            for url in urls
        ]
    )
