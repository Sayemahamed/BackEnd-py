from typing import Optional
from API.exceptions import UserNotFound,IntegrityError
from API.db import get_async_session
from API.schemas import (TokenPayload, URLCreatedResponseSchema,
                         URLCreationSchema)
from API.services import validate_token,validate_token_optional,UserService,URLServices
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import HttpUrl

url_router=APIRouter()

@url_router.post("/",response_model=URLCreatedResponseSchema,description="")
async def shorten_url(url_data:URLCreationSchema,url_service:URLServices=Depends(), user_service:UserService=Depends(), token:Optional[TokenPayload]=Depends(validate_token_optional),session:AsyncSession=Depends(get_async_session))->URLCreatedResponseSchema:
    user=None
    if token is not None:
            user = await user_service.get_user_by_id(token.user_id, session)
            if not user:
                raise UserNotFound().to_http()
    try:         
        url= await url_service.create_url(url_data,user,session)
        return URLCreatedResponseSchema(
            id=url.id,
            short_code=str(url.short_code),
            original_url= url.original_url,
            short_url=str(url.short_code),
            created_at=url.created_at,
            expires_at=url.expires_at
        )
    except IntegrityError as exp:
         raise exp.to_http()