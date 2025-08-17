from os import name
from re import U
from sqlite3 import IntegrityError

from API.db import User, get_async_session
from API.schemas import UserCreationSchema, UserResponseSchema
from API.services import get_password_hash
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    def __init__(self) -> None:
        pass

    async def ger_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.email == email.lower()))
        return user.first()

    async def ger_user_by_id(self, id: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.id == id))
        return user.first()

    async def create_user(
        self, user_data: UserCreationSchema, session: AsyncSession
    ) -> User:
        existing_user = await self.ger_user_by_email(user_data.email, session)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )  # type: ignore
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )
