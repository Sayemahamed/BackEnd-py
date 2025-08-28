from typing import Optional

from API.db import get_async_session
from API.exceptions import IntegrityError,NOSuchURL
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
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

url_router = APIRouter()


@url_router.post("/", response_model=URLCreatedResponseSchema, description="")
async def shorten_url(
    url_data: URLCreationSchema,
    url_service: URLServices = Depends(),
    user_service: UserService = Depends(),
    token: Optional[TokenPayload] = Depends(validate_token),
    session: AsyncSession = Depends(get_async_session),
) -> URLCreatedResponseSchema:
    user = None
    if token is not None:
        user = await user_service.get_user_by_id(token.user_id, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        url = await url_service.create_url(url_data, user, session)
        return URLCreatedResponseSchema(
            id=url.id,
            short_code=str(url.short_code),
            original_url=url.original_url,
            short_url="http://localhost:8000/"+str(url.short_code),
            created_at=url.created_at,
            expires_at=url.expires_at,
        )
    except IntegrityError as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Intern db error")


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    urls = await url_service.get_urls(user, session)
    return URLsSchema(
        urls=[
            URLInfo(
                id=url.id,
                original_url=url.original_url,
                short_url="http://localhost:8000/"+str(url.short_code),
                short_code=str(url.short_code),
                visit_count=url.visit_count,
                created_at=url.created_at,
                expires_at=url.expires_at,
            )
            for url in urls
        ]
    )

@url_router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    short_code: str,
    url_service: URLServices = Depends(),
    user_service: UserService = Depends(),
    token: Optional[TokenPayload] = Depends(validate_token),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        await url_service.delete_url(short_code, user, session)
    except NOSuchURL as ext:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ext.message)
    except IntegrityError :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Intern db error")