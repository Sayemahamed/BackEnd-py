from API.db import User, get_async_session
from API.schemas import UserResponseSchema, UserCreationSchema, UserUpdateSchema, TokenPayload
from API.services import UserService, validate_token
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status
from API.exceptions import UserAlreadyExists,IntegrityError,UserNotFound


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
        raise exp.to_http()
    except IntegrityError as exp:
        raise exp.to_http()

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
    print(token)
    user: User | None = await user_service.get_user_by_id(token.user_id, session)
    if not user:
        raise UserNotFound().to_http()
    return UserResponseSchema(
        id=user.id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        username=user.username,
        email=user.email,
    )
