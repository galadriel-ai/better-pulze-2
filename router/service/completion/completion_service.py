from typing import Dict

import aiohttp
from router import api_logger
from langsmith import traceable
from starlette.responses import JSONResponse

from router import analytics
from router.analytics import TrackingEventType
from router.domain.pricing.entities import UsageDebug
from router.domain.tokens.token_tracker import TokenTracker
from router.repository.user_repository import ValidatedUser
from router.service.completion.entities import ChatCompletionRequest
from router.service.completion.utils import get_chat_completion_endpoint

logger = api_logger.get()


@traceable(run_type="chain", name="CompletionService")
async def execute(
    request: ChatCompletionRequest,
    token_tracker: TokenTracker,
    validated_user: ValidatedUser,
) -> JSONResponse:
    # Clean up etc
    request.model = "mistralai/Mistral-7B-Instruct-v0.1"
    request_input = request.model_dump()

    for m in request_input["messages"]:
        if not m.get("function_call"):
            m.pop("name", None)
            m.pop("function_call", None)

    # OpenAI API is annoying
    formatted_dict = {}
    for key, value in request_input.items():
        if value:
            formatted_dict[key] = value

    status, response_dict, provider = await _get_oai_response(formatted_dict)
    token_tracker.track(validated_user.uid, provider, response_dict)
    analytics.track(
        TrackingEventType.API_REQUEST,
        validated_user.uid,
        validated_user.email,
        tokens=response_dict.get("usage"),
    )
    return JSONResponse(content=response_dict, status_code=status)


@traceable(run_type="llm", name="openai.ChatCompletion.create")
async def _get_oai_response(formatted_dict):
    endpoint = get_chat_completion_endpoint()
    async with aiohttp.ClientSession() as session:
        res = await session.post(
            endpoint.url,
            headers=endpoint.headers,
            json=formatted_dict,
        )
        return res.status, await res.json(), endpoint.name


def _get_usage_response(usage: UsageDebug, usage_type: str) -> Dict:
    return {"type": usage_type, **usage.__dict__}
