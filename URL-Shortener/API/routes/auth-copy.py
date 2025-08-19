from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from API.db import get_async_session
from API.schemas.auth_copy import TokenResponse, TokenRefreshRequest, TokenRefreshResponse
from API.services.auth_copy import (
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
    get_current_user,
)
from API.services.user_service import UserService
from API.exceptions.auth_copy import InvalidCredentials, TokenInvalid, TokenExpired

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Get access and refresh tokens",
    description="Authenticate user and return access and refresh tokens"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """Authenticate user and return tokens"""
    user = await user_service.get_user_by_email(form_data.username, session)
    if not user or not await user_service.verify_password(form_data.password, user.hashed_password):
        raise InvalidCredentials()

    token_data = {"user_id": str(user.id), "scopes": form_data.scopes or []}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@auth_router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a refresh token"
)
async def refresh_token(
    token_data: TokenRefreshRequest,
):
    """Refresh access token using refresh token"""
    try:
        # Validate the refresh token
        payload = validate_refresh_token(token_data.refresh_token)
        
        # Create new tokens
        new_token_data = {
            "user_id": payload.user_id,
            "scopes": payload.scopes or []
        }
        
        access_token = create_access_token(new_token_data)
        refresh_token = create_refresh_token(new_token_data)
        
        return TokenRefreshResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.get(
    "/me",
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def read_users_me(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get current user information"""
    return {"user_id": current_user.user_id, "scopes": current_user.scopes}
