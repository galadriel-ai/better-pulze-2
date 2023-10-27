from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class UsageDebug:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    price: str
    price_currency: Literal["USD"] = "USD"
