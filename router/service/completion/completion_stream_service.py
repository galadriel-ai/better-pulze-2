import json
from typing import List
from typing import AsyncIterable

import aiohttp
from langsmith import traceable

from router import analytics
from router.analytics import TrackingEventType
from router.domain.tokens.token_tracker import TokenTracker
from router.repository.user_repository import ValidatedUser
from router.service.completion.entities import Message
from router.service.completion.entities import BaseMessage
from router.service.completion.entities import ChatCompletionRequest
from router.service.completion.utils import get_chat_completion_endpoint


async def execute(
    request: ChatCompletionRequest,
    token_tracker: TokenTracker,
    validated_user: ValidatedUser,
) -> AsyncIterable:
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
    endpoint = get_chat_completion_endpoint()
    async with aiohttp.ClientSession() as session:
        res = await session.post(
            endpoint.url,
            headers=endpoint.headers,
            json=formatted_dict,
        )
        completion_tokens = 0
        usage = None
        async for line in res.content:
            try:
                decoded = line.decode()
                if decoded[1] != "\n":
                    decoded_line = json.loads(decoded.split("data: ")[-1])
                    if await _has_token(decoded_line):
                        completion_tokens += 1
                    all_lines.append(decoded_line)
                    if decoded_line.get("usage"):
                        usage = decoded_line["usage"]
            except:
                pass

            yield line
        if usage is None:
            prompt_tokens = await _estimate_prompt_len(request.messages)
            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": completion_tokens + prompt_tokens,
            }
        token_tracker.track(
            validated_user.uid, endpoint.name, {"model": request.model, "usage": usage}
        )
        analytics.track(
            TrackingEventType.API_REQUEST,
            validated_user.uid,
            validated_user.email,
            tokens=usage,
        )

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


async def _estimate_prompt_len(messages: List[Message]) -> int:
    token_count = 0
    for message in messages:
        if isinstance(message, BaseMessage):
            token_count += len(message.content or "") // 3
    return token_count


async def _has_token(chunk: dict) -> bool:
    return chunk["choices"][0]["delta"].get("content") is not None
