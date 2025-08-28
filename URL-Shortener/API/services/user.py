from API.db import User
from API.exceptions import (
    EmailAlreadyRegistered,
    IntegrityError,
    UserAlreadyExists,
    WrongPassword,
)
from API.schemas import UserCreationSchema, UserDeleteSchema, UserUpdateSchema
from API.services import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError as alchemy_IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    def __init__(self) -> None:
        pass

    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.email == email.lower()))
        return user.first()

    async def get_user_by_id(self, id: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.id == id))
        return user.first()

    async def create_user(
        self, user_data: UserCreationSchema, session: AsyncSession
    ) -> User:
        existing_user = await self.get_user_by_email(user_data.email, session)
        if existing_user:
            raise EmailAlreadyRegistered(email=user_data.email)
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
        except alchemy_IntegrityError:
            raise IntegrityError

    async def update_user(
        self, user: User, user_data: UserUpdateSchema, session: AsyncSession
    ) -> User:
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.new_password:
            if user_data.previous_password is None or not verify_password(
                user_data.previous_password, user.hashed_password
            ):
                raise WrongPassword(
                    message="Provide current password for password update."
                )
            user.hashed_password = get_password_hash(user_data.new_password)
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except alchemy_IntegrityError:
            raise IntegrityError

    async def delete_user(
        self, user_data: UserDeleteSchema, user: User, session: AsyncSession
    ) -> None:
        if not verify_password(user_data.password, user.hashed_password):
            raise WrongPassword(message="Provide correct password for user deletion.")
        try:
            await session.delete(user)
            await session.commit()
        except alchemy_IntegrityError:
            raise IntegrityError
