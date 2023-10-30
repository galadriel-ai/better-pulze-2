from fastapi import APIRouter

from router import api_logger
from router.repository.user_repository import UserRepositoryFirebase

TAG = "User"
router = APIRouter()
router.tags = [TAG]

logger = api_logger.get()

user_repository = UserRepositoryFirebase()


@router.get(
    "/v1/user",
)
async def endpoint():
    # If user does not exist return 404
    return {
        "user": {
            "uid": "hello"
        }
    }


@router.post(
    "/v1/user"
)
async def create_user():
    return {"hello": "world"}
