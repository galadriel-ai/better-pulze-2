from router.repository.user_repository import UserRepositoryFirebase
from router.service.user.entities import GetUserResponse


def execute(user_uid: str, user_repository: UserRepositoryFirebase) -> GetUserResponse:
    user = user_repository.get_user(user_uid)
    return GetUserResponse(
        email=user.email, api_key=user.api_key, user_role=user.user_role
    )
