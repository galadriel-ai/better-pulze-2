from router.repository.user_repository import UserRepositoryFirebase
from router.service import error_responses
from router.service.user.entities import GetUserResponse


def execute(user_uid: str, user_repository: UserRepositoryFirebase) -> GetUserResponse:
    user = user_repository.get_user(user_uid)
    if user:
        return GetUserResponse(
            email=user.email, api_key=user.api_key, user_role=user.user_role
        )
    raise error_responses.NotFoundAPIError("user")
