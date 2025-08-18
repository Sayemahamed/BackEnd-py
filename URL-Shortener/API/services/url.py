from API.db import ShortURL,User
from sqlalchemy.exc import IntegrityError as alchemy_IntegrityError
from sqlmodel import select
from nanoid import generate
from API.exceptions import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from API.schemas import URLCreationSchema
from API.config import settings
from datetime import datetime,timedelta, timezone
from typing import Optional

class URLServices:
    def __init__(self) -> None:
        pass
    async def create_url(self,url_data:URLCreationSchema,user:Optional[User],session:AsyncSession)->ShortURL:
        url:ShortURL=ShortURL(
            id=None,#type:ignore
            created_at=None,#type:ignore
            visit_count=None,#type:ignore
            short_code=generate("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", 12),
            original_url=str(url_data.original_url),
            user_id=None if user is None else user.id,
            expires_at=datetime.now(timezone.utc)+timedelta(days=settings.URL_EXPIRE_DAYS)
        )
        session.add(url)
        try:
            await session.commit()
            await session.refresh(url)
            return url
        except alchemy_IntegrityError:
            await session.rollback()
            raise IntegrityError
