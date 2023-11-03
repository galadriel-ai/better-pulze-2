import os

from fastapi import APIRouter

from router import api_logger, analytics
from router.analytics import TrackingEventType
from router.repository.user_repository import UserRepositoryFirebase
from router.repository.user_repository import ValidatedUser
from router.service.auth.validate_id_token import SessionTokenValidator
from router.service.auth.validate_id_token import StytchTokenValidator
from router.service.user import create_user_service
from router.service.user import get_user_service
from router.service.user.entities import CreateUserRequest
from router.service.user.entities import GetUserResponse
from fastapi import Depends

TAG = "User"
router = APIRouter()
router.tags = [TAG]

logger = api_logger.get()

user_repository = UserRepositoryFirebase.instance()
session_token_validator: SessionTokenValidator = StytchTokenValidator(
    project_id=os.getenv("STYTCH_PROJECT_ID"),
    secret=os.getenv("STYTCH_SECRET"),
    environment=os.getenv("STYTCH_ENVIRONMENT"),
)


@router.get("/v1/user", response_model=GetUserResponse)
async def get_user(
        validated_user: ValidatedUser = Depends(session_token_validator.validate),
):
    # If user does not exist return 404
    return get_user_service.execute(
        user_uid=validated_user.uid, user_repository=user_repository
    )


@router.post("/v1/user", response_model=GetUserResponse)
async def update_user(
        payload: CreateUserRequest,
        validated_user: ValidatedUser = Depends(session_token_validator.validate),
):
    response = create_user_service.execute(
        validated_user=validated_user, payload=payload, user_repository=user_repository
    )
    analytics.track(TrackingEventType.REGISTER, validated_user.uid, validated_user.email)
    return response
