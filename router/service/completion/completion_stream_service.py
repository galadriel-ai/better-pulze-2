import json
import os
from typing import Dict, AsyncIterable

import aiohttp
from langsmith import traceable

from router.domain.pricing.entities import UsageDebug
from router.service.completion.entities import ChatCompletionRequest
from router.service.completion.intent_router import detect_intent, Intent


async def execute(request: ChatCompletionRequest, authorization=None) -> AsyncIterable:
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

    all_lines = []
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
        async for line in res.content:
            try:
                decoded = line.decode()
                if decoded[1] != "\n":
                    all_lines.append(json.loads(decoded.split("data: ")[-1]))
            except:
                pass
            yield line

    @traceable(run_type="llm", name="stream_openai.ChatCompletion.create")
    def trace(r):
        try:
            model = all_lines[0]["model"]
            content = "".join(
                [l["choices"][0]["delta"].get("content", "") for l in all_lines]
            )
            return model, content
        except:
            return "", ""

    trace(request)
