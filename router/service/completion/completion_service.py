import os
from _decimal import Decimal
from typing import Dict

import aiohttp
from starlette.responses import JSONResponse

from router.domain.pricing import calculate_tokens_price
from router.service.completion.entities import ChatCompletionRequest
from router.service.completion.intent_router import detect_intent, Intent


async def execute(request: ChatCompletionRequest, authorization=None) -> JSONResponse:
    # Clean up etc
    request.model = "gpt-4"  # TODO: pick model in a smart way :)
    request_input = request.model_dump()
    intent, intent_price = detect_intent(request_input["messages"][-1]["content"])
    if intent == Intent.REASONING:
        request.model = "gpt-4"
    else:
        request.model = "gpt-3.5-turbo-16k"
    for m in request_input["messages"]:
        if not m.get("function_call"):
            m.pop("name", None)
            m.pop("function_call", None)

    # OpenAI API is annoying
    formatted_dict = {}
    for key, value in request_input.items():
        if value:
            formatted_dict[key] = value

    response = await _get_oai_response(authorization, formatted_dict)
    response_dict: Dict = await response.json()
    price = calculate_tokens_price.cost_from_api_response(response_dict)
    response_dict["price"] = str(Decimal(price) + Decimal(intent_price))
    response_dict["price_currency"] = "USD"
    return JSONResponse(content=response_dict, status_code=response.status)


async def _get_oai_response(authorization, formatted_dict):
    async with aiohttp.ClientSession() as session:
        return await session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": authorization if authorization else f'Bearer {os.getenv("OPENAI_API_KEY")}'
            },
            json=formatted_dict
        )
