import time
from prometheus_client import Counter, Histogram
from prometheus_client import Summary
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from router import api_logger
from router.service.error_responses import APIErrorResponse
from router.service.monitoring.utils import get_path_template

REQUESTS = Counter(
    "llm_proxy_requests_total",
    "Total count of requests by method and path.",
    ["method", "path_template"],
)
RESPONSES = Counter(
    "llm_proxy_responses_total",
    "Total count of responses by method, path and status codes.",
    ["method", "path_template", "status_code"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    "llm_proxy_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path_template"],
)
REQUESTS_PROCESSING_TIME_ERRORS = Summary(
    "llm_proxy_error_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path_template", "exception_type"],
)
EXCEPTIONS = Counter(
    "llm_proxy_exceptions_total",
    "Total count of exceptions raised by path and exception type",
    ["method", "path_template", "exception_type", "is_unexpected"],
)
LLM_COMPLETION_TOKENS_GENERATED = Summary(
    "llm_proxy_llm_completion_tokens",
    "Histogram of llm completion tokens",
    ["method", "path_template", "model_name"],
)
LLM_PROMPT_TOKENS_GENERATED = Summary(
    "llm_proxy_llm_prompt_tokens",
    "Histogram of llm prompt tokens",
    ["method", "path_template", "model_name"],
)
LLM_TOTAL_TOKENS_GENERATED = Summary(
    "llm_proxy_llm_total_tokens",
    "Histogram of llm total tokens",
    ["method", "path_template", "model_name"],
)

logger = api_logger.get()


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, filter_unhandled_paths: bool = False) -> None:
        super().__init__(app)
        self.filter_unhandled_paths = filter_unhandled_paths

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.time()
        method = request.method
        path_template, is_handled_path = get_path_template(request)
        if self._is_path_filtered(is_handled_path):
            return await call_next(request)
        REQUESTS.labels(method=method, path_template=path_template).inc()
        before_time = time.perf_counter()
        time_elapsed = time.time() - start
        if time_elapsed > 1:
            logger.debug(f"Middleware Prometheus before request time: {time_elapsed}")
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = self.get_status_code(e)
            is_unexpected = status_code >= 500
            EXCEPTIONS.labels(
                method=method,
                path_template=path_template,
                is_unexpected=is_unexpected,
                exception_type=type(e).__name__,
            ).inc()
            after_time = time.perf_counter()
            REQUESTS_PROCESSING_TIME_ERRORS.labels(
                method=method,
                exception_type=type(e).__name__,
                path_template=path_template,
            ).observe(after_time - before_time)
            raise e
        else:
            start = time.time()
            status_code = response.status_code
            after_time = time.perf_counter()
            REQUESTS_PROCESSING_TIME.labels(
                method=method, path_template=path_template
            ).observe(after_time - before_time)
        finally:
            RESPONSES.labels(
                method=method,
                path_template=path_template,
                status_code=status_code,
            ).inc()
            time_elapsed = time.time() - start
            if time_elapsed > 1:
                logger.debug(
                    f"Middleware Prometheus after request time: {time_elapsed}"
                )
        return response

    def _is_path_filtered(self, is_handled_path: bool) -> bool:
        return self.filter_unhandled_paths and not is_handled_path

    @staticmethod
    def get_status_code(ex: BaseException) -> int:
        """
        We can be throwing "expected" exceptions that are not internal server errors,
        but carrying non-2xx response codes.
        Take a look at APIErrorResponse errors.
        """
        if isinstance(ex, APIErrorResponse):
            return ex.to_status_code()
        return HTTP_500_INTERNAL_SERVER_ERROR
