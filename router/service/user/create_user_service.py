from router.domain.user.entities import User
from router.repository.user_repository import UserRepositoryFirebase
from router.repository.user_repository import ValidatedUser
from router.service.user.entities import CreateUserRequest
from router.service.user.entities import GetUserResponse


def execute(
    validated_user: ValidatedUser,
    payload: CreateUserRequest,
    user_repository: UserRepositoryFirebase,
) -> GetUserResponse:
    user_repository.create_user(
        User(
            uid=validated_user.uid,
            email=validated_user.email,
            api_key="MOCK-KEY",  # TODO: create proper
            user_role=payload.user_role,
        )
    )
    user = user_repository.get_user(validated_user.uid)
    return GetUserResponse(
        email=user.email, api_key=user.api_key, user_role=user.user_role
    )
