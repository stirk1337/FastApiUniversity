import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool

import config
from src.db.models import Base
from main import app
from src.db.session import get_db

engine = create_async_engine(str(config.settings.postgres_test), poolclass=NullPool)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = Base.metadata
metadata.bind = engine


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)



# @pytest.fixture(autouse=True, scope='session')
# async def prepare_database():
#     os.system('alembic init migrations')
#     os.system('alembic revision --autogenerate -m "test running migrations"')
#     os.system('alembic upgrade heads')


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac




