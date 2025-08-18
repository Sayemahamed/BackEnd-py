from API.db import User
from API.schemas import UserCreationSchema
from API.services import get_password_hash
from sqlmodel import select
from sqlalchemy.exc import IntegrityError as alchemy_IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from API.exceptions import UserAlreadyExists,IntegrityError


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
            raise UserAlreadyExists
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
            await session.rollback()
            raise IntegrityError
