from typing import Optional

from fastapi import Security
from fastapi.security import APIKeyHeader

from router.repository.user_repository import UserRepositoryFirebase
from router.service import error_responses

API_KEY_NAME = "Authorization"
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class IdTokenValidator:
    def __init__(self, user_repository: UserRepositoryFirebase):
        self.user_repository = user_repository

    async def validate(
        self, api_key_header: str = Security(API_KEY_HEADER)
    ) -> Optional[str]:
        try:
            if not api_key_header:
                raise error_responses.AuthorizationMissingAPIError()

            validated_user = self.user_repository.validate_user(api_key_header)
            return validated_user
        except Exception as exc:
            raise error_responses.InvalidCredentialsAPIError()


class ApiKeyValidator:
    def __init__(self, user_repository: UserRepositoryFirebase):
        self.user_repository = user_repository

    async def validate(
        self, api_key_header: str = Security(API_KEY_HEADER)
    ) -> Optional[str]:
        try:
            if not api_key_header:
                raise error_responses.AuthorizationMissingAPIError()

            result = self.user_repository.validate_api_key(api_key_header)
            if result:
                return result
        except Exception as exc:
            pass
        raise error_responses.InvalidCredentialsAPIError()
