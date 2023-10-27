from fastapi import APIRouter, Header
from starlette.responses import StreamingResponse

from router import api_logger
from router.service.completion import completion_service, completion_stream_service
from router.service.completion.entities import ChatCompletionRequest, ChatCompletionResponse

TAG = "Router"
router = APIRouter()
router.openapi_tags = [TAG]
router.title = "Router router"

logger = api_logger.get()


@router.post(
    "/v1/chat/completions",
    # response_model=ChatCompletionResponse,
)
async def endpoint(
        request: ChatCompletionRequest,
        authorization: str = Header(None)
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
