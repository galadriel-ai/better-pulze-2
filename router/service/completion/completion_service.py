import os
from _decimal import Decimal
from typing import Dict

import aiohttp
from langsmith import traceable
from starlette.responses import JSONResponse

from router.domain.pricing import calculate_tokens_price
from router.domain.pricing.entities import UsageDebug
from router.service.completion.entities import ChatCompletionRequest
from router.service.completion.intent_router import detect_intent, Intent


@traceable(run_type="chain", name="CompletionService")
async def execute(request: ChatCompletionRequest, authorization=None) -> JSONResponse:
    # Clean up etc
    request.model = "gpt-4"
    request_input = request.model_dump()
    intent, intent_usage = detect_intent(request_input["messages"][-1]["content"])
    if intent == Intent.REASONING:
        request_input["model"] = "gpt-4"
    else:
        request_input["model"] = "gpt-3.5-turbo-16k"
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
    usage = calculate_tokens_price.cost_from_api_response(response_dict)
    response_dict["price"] = str(Decimal(usage.price) + Decimal(intent_usage.price))
    response_dict["price_currency"] = usage.price_currency
    response_dict["usage_debug"] = [
        _get_usage_response(intent_usage, "intent"),
        _get_usage_response(usage, "completion"),
    ]
    return JSONResponse(content=response_dict, status_code=status)


@traceable(run_type="llm", name="openai.ChatCompletion.create")
async def _get_oai_response(authorization, formatted_dict):
    async with aiohttp.ClientSession() as session:
        res = await session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": authorization
                if authorization
                else f'Bearer {os.getenv("OPENAI_API_KEY")}'
            },
            json=formatted_dict,
        )
        return res.status, await res.json()


def _get_usage_response(usage: UsageDebug, usage_type: str) -> Dict:
    return {"type": usage_type, **usage.__dict__}
