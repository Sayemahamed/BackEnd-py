from os import name
from API.db import User, get_async_session
from API.schemas import UserResponseSchema, UserCreationSchema, UserUpdateSchema
from API.services import UserService, validate_token
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status


user_router = APIRouter()


@user_router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def create_user(
    user_data: UserCreationSchema,
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> UserResponseSchema:
    user = await user_service.create_user(user_data, session)
    return UserResponseSchema(
        id=user.id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        username=user.username,
        email=user.email,
    )
