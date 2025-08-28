from datetime import datetime, timedelta, timezone
from typing import Optional

from API.config import settings
from API.db import ShortURL, User
from API.exceptions import IntegrityError,NOSuchURL
from API.schemas import URLCreationSchema
from nanoid import generate
from sqlalchemy.exc import IntegrityError as alchemy_IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class URLServices:
    def __init__(self) -> None:
        pass

    async def create_url(
        self, url_data: URLCreationSchema, user: Optional[User], session: AsyncSession
    ) -> ShortURL:
        url: ShortURL = ShortURL(
            id=None,  # type:ignore
            created_at=None,  # type:ignore
            visit_count=None,  # type:ignore
            short_code=generate(
                settings.NANO_CODE_STRING, 12
            ),
            original_url=str(url_data.original_url),
            user_id=None if user is None else user.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.URL_EXPIRE_DAYS),
        )
        session.add(url)
        try:
            await session.commit()
            await session.refresh(url)
            return url
        except alchemy_IntegrityError:
            raise IntegrityError

    async def get_urls(self, user: User, session: AsyncSession):
        urls = await session.exec(select(ShortURL).where(ShortURL.user_id == user.id))
        return urls
    
    async def delete_url(self, short_code: str, user: User, session: AsyncSession):
        url = await session.exec(select(ShortURL).where(ShortURL.short_code == short_code))
        url = url.first()
        if url is None:
            # print("No such url")
            raise NOSuchURL()
        if url.user_id != user.id:
            raise NOSuchURL("You are not the owner of the url")
        try:
            await session.delete(url)
            await session.commit()
        except alchemy_IntegrityError:
            raise IntegrityError