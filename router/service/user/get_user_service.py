from router.domain.user.entities import User
from router.repository.user_repository import UserRepositoryFirebase
from router.service import error_responses
from router.service.user.entities import GetUserResponse


def execute(user_uid: str, user_repository: UserRepositoryFirebase) -> GetUserResponse:
    user: User = user_repository.get_user(user_uid)
    if user:
        return GetUserResponse.from_user(user)
    raise error_responses.NotFoundAPIError("user")
