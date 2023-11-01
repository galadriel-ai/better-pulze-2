import os
from typing import Dict

import aiohttp
from langsmith import traceable
from starlette.responses import JSONResponse

from router.domain.pricing.entities import UsageDebug
from router.domain.tokens.token_tracker import TokenTracker
from router.service.completion.entities import ChatCompletionRequest


@traceable(run_type="chain", name="CompletionService")
async def execute(request: ChatCompletionRequest, token_tracker: TokenTracker, authorization=None) -> JSONResponse:
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

    status, response_dict = await _get_oai_response(authorization, formatted_dict)
    return JSONResponse(content=response_dict, status_code=status)


@traceable(run_type="llm", name="openai.ChatCompletion.create")
async def _get_oai_response(authorization, formatted_dict):
    async with aiohttp.ClientSession() as session:
        res = await session.post(
            "https://api.endpoints.anyscale.com/v1/chat/completions",
            headers={
                "Authorization": authorization
                if authorization
                else f'Bearer {os.getenv("ANYSCALE_LLM_API_KEY")}'
            },
            json=formatted_dict,
        )
        return res.status, await res.json()


def _get_usage_response(usage: UsageDebug, usage_type: str) -> Dict:
    return {"type": usage_type, **usage.__dict__}
