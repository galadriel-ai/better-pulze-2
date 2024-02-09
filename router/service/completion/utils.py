import os
import random
from dataclasses import dataclass
from settings import LLM_BASE_URL, PROVIDER_RATIO


@dataclass(frozen=True)
class ChatCompletionEndpoint:
    name: str
    url: str
    headers: dict = None


def get_chat_completion_endpoint() -> ChatCompletionEndpoint:
    if random.random() < PROVIDER_RATIO:
        return ChatCompletionEndpoint(
            name="perplexity",
            url="https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f'Bearer {os.getenv("PERPLEXITY_API_KEY")}'},
        )
    return ChatCompletionEndpoint(
        name="llmOS_vllm", url=f"{LLM_BASE_URL}chat/completions"
    )
