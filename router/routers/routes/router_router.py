from fastapi import APIRouter, Header

from router import api_logger
from router.service.completion import completion_service
from router.service.completion.entities import ChatCompletionRequest, ChatCompletionResponse

TAG = "Router"
router = APIRouter()
router.openapi_tags = [TAG]
router.title = "Router router"

logger = api_logger.get()


@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
)
async def endpoint(
        request: ChatCompletionRequest,
        authorization: str = Header(None)
):
    return await completion_service.execute(request)

