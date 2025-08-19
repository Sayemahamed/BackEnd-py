from API.db import get_async_session,ShortURL
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
class MainService:
    def __init__(self):
        pass
    async def redirect(self,code: str, session: AsyncSession):
        url= await session.exec(select(ShortURL).where(ShortURL.short_code == code))
        url = url.first()
        if url is None:
            return None
        return url.original_url