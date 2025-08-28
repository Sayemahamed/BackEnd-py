from API.db import ShortURL
from API.celery import prepare_report
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class MainService:
    def __init__(self):
        pass

    async def redirect(self, code: str,user_data:dict, session: AsyncSession):
        url = await session.exec(select(ShortURL).where(ShortURL.short_code == code))
        url = url.first()
        if url is None:
            return None
        user_data.update({"short_url_id": url.id.hex})
        prepare_report.delay(user_data)
        return url.original_url
