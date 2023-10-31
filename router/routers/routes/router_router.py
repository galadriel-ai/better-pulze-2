import time

from fastapi import APIRouter, Header
from fastapi import Depends
from starlette.responses import StreamingResponse

from router import api_logger
from router.repository.user_repository import UserRepositoryFirebase
from router.repository.user_repository import ValidatedUser
from router.service.auth.validate_id_token import ApiKeyValidator
from router.service.completion import completion_service, completion_stream_service
from router.service.completion.entities import (
    ChatCompletionRequest,
)

TAG = "Router"
router = APIRouter()
router.tags = [TAG]

logger = api_logger.get()

user_repository = UserRepositoryFirebase.instance()
api_key_validator = ApiKeyValidator(user_repository)


@router.post(
    "/v1/chat/completions",
)
async def endpoint(
    request: ChatCompletionRequest,
    validated_user: ValidatedUser = Depends(api_key_validator.validate),
):
    if not request.stream:
        return await completion_service.execute(request)
    else:
        headers = {
            "X-Content-Type-Options": "nosniff",
            "Connection": "keep-alive",
        }
        return StreamingResponse(
            completion_stream_service.execute(request),
            headers=headers,
            media_type="text/event-stream",
        )
