from fastapi import APIRouter
from fastapi import Depends
from starlette.responses import StreamingResponse

from router import api_logger, analytics
from router.analytics import TrackingEventType
from router.domain.tokens.token_tracker import TokenTracker
from router.repository.token_usage_repository import TokenUsageRepositoryFirestore
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
token_usage_repository = TokenUsageRepositoryFirestore.instance()


@router.post(
    "/v1/chat/completions",
)
async def endpoint(
    request: ChatCompletionRequest,
    validated_user: ValidatedUser = Depends(api_key_validator.validate),
):
    token_tracker = TokenTracker(
        method="POST",
        path_template="/v1/chat/completions",
        repository=token_usage_repository,
    )
    analytics.track(TrackingEventType.API_REQUEST, validated_user.uid, validated_user.email)
    if not request.stream:
        return await completion_service.execute(request, token_tracker)
    else:
        headers = {
            "X-Content-Type-Options": "nosniff",
            "Connection": "keep-alive",
        }
        return StreamingResponse(
            completion_stream_service.execute(request, token_tracker),
            headers=headers,
            media_type="text/event-stream",
        )
