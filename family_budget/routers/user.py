from family_budget.auth.service import get_current_user, get_password_hash
from family_budget.crud.user import create_user, query_user
from family_budget.deps import Context, get_context
from family_budget.schemas.user import User, UserCreate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

router = APIRouter(prefix="/users")


@router.get("/current", tags=["current user"], description="Get current user", status_code=status.HTTP_200_OK)
async def default(current_user: User = Depends(get_current_user)) -> User:
    return User(username=current_user.username)


@router.post(
    "/", tags=["user registration"], description="Register the user", status_code=status.HTTP_201_CREATED
)
async def user_create(user: UserCreate, context: Context = Depends(get_context)) -> User:
    user_already_exists = query_user(context.session_factory, user.username) is not None
    if user_already_exists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User with that username already exists"
        )
    create_user(context.session_factory, user.username, get_password_hash(user.password))
    return User(username=user.username)
