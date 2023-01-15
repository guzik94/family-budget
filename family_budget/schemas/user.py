from pydantic import BaseModel, validator


class User(BaseModel):
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
