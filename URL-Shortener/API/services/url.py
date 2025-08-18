from sqlalchemy.exc import IntegrityError as alchemy_IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from API.db import ShortURL