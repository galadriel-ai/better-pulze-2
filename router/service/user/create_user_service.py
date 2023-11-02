import secrets

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
            api_key=_create_api_key(),
            name=payload.name,
            user_role=payload.user_role,
            building=payload.building,
            has_paying_customers=payload.has_paying_customers,
            project_stage=payload.project_stage,
            llm_monthly_cost=payload.llm_monthly_cost,
        )
    )
    user = user_repository.get_user(validated_user.uid)
    return GetUserResponse.from_user(user)


def _create_api_key():
    def is_last_4_digits_alpha(_secret):
        return (
            _secret[-1].isalpha()
            and _secret[-2].isalpha()
            and _secret[-3].isalpha()
            and _secret[-4].isalpha()
        )

    while True:
        secret = secrets.token_urlsafe(36)
        if secret[0].isalpha() and is_last_4_digits_alpha(secret):
            return "lo-" + secret
