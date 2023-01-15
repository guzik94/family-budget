from family_budget.auth.service import get_current_user, get_password_hash
from family_budget.crud.user import add_user, query_user
from family_budget.deps import Context, get_context
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.user import User, UserCreate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

router = APIRouter(prefix="/users")


@router.get("/current", tags=["current user"], description="Get current user", status_code=status.HTTP_200_OK)
async def get_user(current_user: UserInDB = Depends(get_current_user)) -> User:
    return User(username=current_user.username)


@router.post("/", tags=["user registration"], description="Register the user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, context: Context = Depends(get_context)) -> User:
    user_already_exists = query_user(context.session_factory, user.username) is not None
    if user_already_exists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This username has already been taken"
        )
    add_user(context.session_factory, user.username, get_password_hash(user.password))
    return User(username=user.username)
