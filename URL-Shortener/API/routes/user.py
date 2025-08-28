from API.db import User, get_async_session
from API.exceptions import (
    IntegrityError,
    UserAlreadyExists,
    WrongPassword,
)
from API.schemas import (
    TokenPayload,
    UserCreationSchema,
    UserDeleteSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from API.services import UserService, validate_token
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

user_router = APIRouter()


@user_router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def create_user(
    user_data: UserCreationSchema,
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> UserResponseSchema:
    try:
        user = await user_service.create_user(user_data, session)
        return UserResponseSchema(
            id=user.id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            username=user.username,
            email=user.email,
        )
    except UserAlreadyExists as exp:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{exp.email} {exp.message}")
    except IntegrityError as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Intern db error")


@user_router.get(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current user info",
)
async def get_current_user(
    user_service: UserService = Depends(),
    token: TokenPayload = Depends(validate_token),
    session: AsyncSession = Depends(get_async_session),
) -> UserResponseSchema:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user: User | None = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponseSchema(
        id=user.id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        username=user.username,
        email=user.email,
    )


@user_router.patch(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update current user info",
)
async def update_current_user(
    user_data: UserUpdateSchema,
    user_service: UserService = Depends(),
    token: TokenPayload = Depends(validate_token),
    session: AsyncSession = Depends(get_async_session),
) -> UserResponseSchema:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user: User | None = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        updated_user = await user_service.update_user(user, user_data, session)
        return UserResponseSchema(
            id=updated_user.id,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            username=updated_user.username,
            email=updated_user.email,
        )
    except WrongPassword as exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exp.message)
    except IntegrityError as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Intern db error")


@user_router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
)
async def delete_current_user(
    user_data: UserDeleteSchema,
    user_service: UserService = Depends(),
    token: TokenPayload = Depends(validate_token),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user: User | None = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        await user_service.delete_user(user_data, user, session)
    except WrongPassword as exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exp.message)
    except IntegrityError as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Intern db error")
