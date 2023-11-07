import os
import random
from dataclasses import dataclass
from settings import LLM_BASE_URL


@dataclass(frozen=True)
class ChatCompletionEndpoint:
    url: str
    headers: dict = None


def get_chat_completion_endpoint() -> ChatCompletionEndpoint:
    if random.random() < 0.5:
        return ChatCompletionEndpoint(
            url="https://api.endpoints.anyscale.com/v1/chat/completions",
            headers={"Authorization": f'Bearer {os.getenv("ANYSCALE_LLM_API_KEY")}'},
        )
    return ChatCompletionEndpoint(url=f"{LLM_BASE_URL}chat/completions")
