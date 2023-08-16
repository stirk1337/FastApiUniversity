from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings

# create async engine
engine = create_async_engine(str(settings.postgres), echo=True)

# create async session
async_session = sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
