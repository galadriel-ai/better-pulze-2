from typing import Dict
from decimal import *

from router.domain.pricing.entities import UsageDebug

price1K = {
    "text-ada-001": "0.0004",
    "text-babbage-001": "0.0005",
    "text-curie-001": "0.002",
    "code-cushman-001": "0.024",
    "code-davinci-002": "0.1",
    "text-davinci-002": "0.02",
    "text-davinci-003": "0.02",
    "gpt-3.5-turbo": ("0.0015", "0.002"),
    "gpt-3.5-turbo-0301": ("0.0015", "0.002"),  # deprecate in Sep
    "gpt-3.5-turbo-0613": ("0.0015", "0.002"),
    "gpt-3.5-turbo-16k": ("0.003", "0.004"),
    "gpt-3.5-turbo-16k-0613": ("0.003", "0.004"),
    "gpt-35-turbo": "0.002",
    "gpt-4": ("0.03", "0.06"),
    "gpt-4-32k": ("0.06", "0.12"),
    "gpt-4-0314": ("0.03", "0.06"),  # deprecate in Sep
    "gpt-4-32k-0314": ("0.06", "0.12"),  # deprecate in Sep
    "gpt-4-0613": ("0.03", "0.06"),
    "gpt-4-32k-0613": ("0.06", "0.12"),
}


def cost(model: str, n_input_tokens: int, n_output_tokens: int) -> UsageDebug:
    """Compute the cost of an API call.

    Args:
        model (str): model name.
        n_input_tokens (int): Input tokens count.
        n_output_tokens (int): Input tokens count.

    Returns:
        The cost in USD. 0 if the model is not supported.
    """
    if model not in price1K:
        return UsageDebug(
            model=model,
            prompt_tokens=n_input_tokens,
            completion_tokens=n_output_tokens,
            total_tokens=n_input_tokens + n_output_tokens,
            price="0",
        )
    pricing = price1K[model]
    if isinstance(pricing, tuple):
        price = str(
            (
                Decimal(pricing[0]) * n_input_tokens
                + Decimal(pricing[1]) * n_output_tokens
            )
            / Decimal(1000)
        )
    else:
        price = str(
            Decimal(pricing) * Decimal(n_input_tokens + n_output_tokens) / Decimal(1000)
        )
    return UsageDebug(
        model=model,
        prompt_tokens=n_input_tokens,
        completion_tokens=n_output_tokens,
        total_tokens=n_input_tokens + n_output_tokens,
        price=price,
    )


def cost_from_api_response(response: Dict) -> UsageDebug:
    """Compute the cost of an API call.

    Args:
        response (dict): The response from OpenAI API.

    Returns:
        The cost in USD. 0 if the model is not supported.
    """
    model = response["model"]
    usage = response["usage"]
    n_input_tokens = usage["prompt_tokens"]
    n_output_tokens = usage.get("completion_tokens", 0)
    return cost(model, n_input_tokens, n_output_tokens)
