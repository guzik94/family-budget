from family_budget.auth.service import get_current_user, get_password_hash
from family_budget.crud.user import add_user, query_user
from family_budget.deps import get_db
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.user import User, UserCreate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users")


@router.get("/current", tags=["current user"], description="Get current user", status_code=status.HTTP_200_OK)
async def get_user(current_user: UserInDB = Depends(get_current_user)) -> User:
    return User.parse_obj(current_user)


@router.post("/", tags=["user registration"], description="Register the user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: Session = Depends(get_db)) -> User:
    user_already_exists = query_user(session, user.username) is not None
    if user_already_exists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This username has already been taken"
        )
    user_id = add_user(session, user.username, get_password_hash(user.password))
    return User(id=user_id, username=user.username)
