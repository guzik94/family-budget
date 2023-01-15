from family_budget.schemas.user import User
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(User):
    id: int
    hashed_password: str
