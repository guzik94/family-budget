from pydantic import BaseModel, validator

from .base import SchemaBase


class User(SchemaBase):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v

    @validator("password")
    def password_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v


class UserShareCreate(BaseModel):
    username: str
