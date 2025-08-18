from typing import Optional

from API.db import get_async_session
from API.schemas import (TokenPayload, URLCreatedResponseSchema,
                         URLCreationSchema)
from API.services import validate_token,validate_token_optional
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

url_router=APIRouter()

@url_router.post("/",response_model=URLCreatedResponseSchema,description="")
async def shorten_url(url_data:URLCreationSchema,token:Optional[TokenPayload]=Depends(validate_token_optional),session:AsyncSession=Depends(get_async_session))->URLCreatedResponseSchema:
