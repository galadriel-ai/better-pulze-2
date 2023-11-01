from typing import Dict

from router import api_logger
from router.repository.token_usage_repository import TokenUsageRepositoryFirestore
from router.service.monitoring.prometheus_middleware import (
    LLM_COMPLETION_TOKENS_GENERATED,
)
from router.service.monitoring.prometheus_middleware import LLM_PROMPT_TOKENS_GENERATED
from router.service.monitoring.prometheus_middleware import LLM_TOTAL_TOKENS_GENERATED

logger = api_logger.get()


class TokenTracker:
    def __init__(
        self,
        method: str,  # GET || POST etc..
        path_template: str,  # /v1/endpoint
        repository: TokenUsageRepositoryFirestore,
    ):
        self.method = method
        self.path_template = path_template
        self.repository = repository

    def track(self, response_dict: Dict):
        try:
            model_name = response_dict["model"]
            usage = response_dict["usage"]

            LLM_COMPLETION_TOKENS_GENERATED.labels(
                method=self.method,
                path_template=self.path_template,
                model_name=model_name,
            ).observe(usage["completion_tokens"])

            LLM_PROMPT_TOKENS_GENERATED.labels(
                method=self.method,
                path_template=self.path_template,
                model_name=model_name,
            ).observe(usage["prompt_tokens"])

            LLM_TOTAL_TOKENS_GENERATED.labels(
                method=self.method,
                path_template=self.path_template,
                model_name=model_name,
            ).observe(usage["total_tokens"])

            self.repository.track(model_name, usage)
        except Exception as exc:
            # Log exception
            logger.info(f"Token tracker exception: {exc}")
