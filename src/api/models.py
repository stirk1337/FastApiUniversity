import uuid

import pydantic
from pydantic import BaseModel, EmailStr


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
