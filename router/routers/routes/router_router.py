import os

import requests
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from router import api_logger
from router.service.completion.entities import ChatCompletionRequest, ChatCompletionResponse
from router.service.completion.intent_router import Intent
from router.service.completion.intent_router import detect_intent
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
    # Clean up etc
    request.model = "gpt-4"  # TODO: pick model in a smart way :)
    request_input = request.model_dump()
    intent = detect_intent(request_input["messages"][-1]["content"])
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

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": authorization if authorization else f'Bearer {os.getenv("OPENAI_API_KEY")}'
        },
        json=formatted_dict
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

