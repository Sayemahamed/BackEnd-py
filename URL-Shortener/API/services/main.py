from API.db import ShortURL, get_async_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class MainService:
    def __init__(self):
        pass

    async def redirect(self, code: str, session: AsyncSession):
        url = await session.exec(select(ShortURL).where(ShortURL.short_code == code))
        url = url.first()
        if url is None:
            return None
        return url.original_url
