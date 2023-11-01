from abc import ABC
from abc import abstractmethod
from typing import Optional

from fastapi import Security
from fastapi.security import APIKeyHeader
from stytch import Client
from stytch.consumer.models.sessions import AuthenticateResponse

from router import api_logger
from router.repository.user_repository import UserRepositoryFirebase
from router.repository.user_repository import ValidatedUser
from router.service import error_responses

API_KEY_NAME = "Authorization"
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

logger = api_logger.get()


class SessionTokenValidator(ABC):
    @abstractmethod
    async def validate(
        self, api_key_header: str = Security(API_KEY_HEADER)
    ) -> Optional[ValidatedUser]:
        pass


class StytchTokenValidator(SessionTokenValidator):
    def __init__(self, project_id: str, secret: str, environment: str = "test"):
        self.client = Client(
            project_id=project_id,
            secret=secret,
            environment=environment,
        )

    async def validate(
        self, api_key_header: str = Security(API_KEY_HEADER)
    ) -> Optional[ValidatedUser]:
        try:
            if not api_key_header:
                raise error_responses.AuthorizationMissingAPIError()

            resp: AuthenticateResponse = self.client.sessions.authenticate(
                session_token=api_key_header
            )
            user = resp.user
            return ValidatedUser(uid=user.user_id, email=user.emails[0].email)
        except Exception as exc:
            logger.debug(f"StytchTokenValidator.validate exception: {exc}")
            raise error_responses.InvalidCredentialsAPIError()


class ApiKeyValidator:
    def __init__(self, user_repository: UserRepositoryFirebase):
        self.user_repository = user_repository

    async def validate(
        self, api_key_header: str = Security(API_KEY_HEADER)
    ) -> Optional[ValidatedUser]:
        if not api_key_header:
            raise error_responses.AuthorizationMissingAPIError()

        if not api_key_header.startswith("Bearer "):
            raise error_responses.InvalidCredentialsAPIError(
                message_extra="Authorization header needs to start with 'Bearer '"
            )

        api_key_header = api_key_header.replace("Bearer ", "")
        if not api_key_header.startswith("lo-"):
            raise error_responses.InvalidCredentialsAPIError(
                message_extra="API Key needs to start with 'lo-'. Please make sure "
                "you using llmos.dev API Key."
            )

        result = self.user_repository.validate_api_key(api_key_header)
        if result:
            return result
        raise error_responses.InvalidCredentialsAPIError(
            message_extra="API Key not found."
        )
