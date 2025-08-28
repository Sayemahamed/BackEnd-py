from API.db import get_async_session
from API.schemas import TokenResponse
from API.services import UserService, create_access_token, verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

auth_router = APIRouter()


@auth_router.post("/token", response_model=TokenResponse)
async def get_token_for_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.get_user_by_email(form_data.username, session)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"user_id": user.id.hex})
    return TokenResponse(access_token=access_token, token_type="bearer")
