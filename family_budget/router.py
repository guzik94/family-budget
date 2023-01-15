from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/")
async def default() -> dict:
    return {"message": "Hello world"}
