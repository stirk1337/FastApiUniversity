import uuid
from typing import AsyncGenerator

import pydantic
import uvicorn
from pydantic import BaseModel, EmailStr
from sqlalchemy import UUID, Column, String, Boolean

from config import settings
from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


# create async engine
engine = create_async_engine(str(settings.postgres), echo=True)

# create async session
async_session = sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)


# default model class
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str, surname: str, email: str) -> User:
        new_user = User(name=name, surname=surname, email=email)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""
        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: pydantic.constr(pattern="^[а-яА-Яa-zA-Z\-]+$")
    surname: pydantic.constr(pattern="^[а-яА-Яa-zA-Z\-]+$")
    email: EmailStr


app = FastAPI()

user_router = APIRouter()


async def _create_new_user(body: UserCreate) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(name=body.name, surname=body.surname, email=body.email)
            return ShowUser(user_id=user.user_id, name=user.name, surname=user.surname, email=user.email,
                            is_active=user.is_active)


@user_router.post('/', response_model=ShowUser)
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)


main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix='/user', tags=['user'])
app.include_router(main_api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
