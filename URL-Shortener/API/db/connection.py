from typing import Any, AsyncGenerator

from API.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

engine: AsyncEngine = create_async_engine(
    url=settings.POSTGRES_URL_ASYNC,
    echo=True,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    pool_recycle=settings.POOL_RECYCLE,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    """Dependency function that yields an async session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def init_db():
    async with engine.begin() as conn:
        try:
            from API.db.models import User
            await conn.run_sync(SQLModel.metadata.create_all)
        except Exception:
            raise