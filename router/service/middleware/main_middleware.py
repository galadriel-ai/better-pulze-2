from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

import settings
from router import api_logger
from router.repository.demo_user_repository import DemoUserRepositoryFirebase
from router.service.error_responses import APIErrorResponse
from router.service.error_responses import RateLimitExceededAPIError
from router.service.middleware import util
from router.service.middleware.entitites import RequestStateKey
from router.service.middleware.rate_limiter import RateLimiter
from router.utils.http_headers import add_response_headers
import time

logger = api_logger.get()

usage_repository = DemoUserRepositoryFirebase.instance()
rate_limiter = RateLimiter(
    max_calls_per_hour=settings.DEMO_API_KEY_ALLOWED_USAGE,
    usage_repository=usage_repository,
)


class MainMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = util.get_state(request, RequestStateKey.REQUEST_ID)
        ip_address = util.get_state(request, RequestStateKey.IP_ADDRESS)
        country = util.get_state(request, RequestStateKey.COUNTRY)

        api_key = request.headers.get("authorization")
        formatted_ip = ip_address or request.client.host or "default"
        logger.info(f"REQUEST RATE LIMITTING INFO: " f" {str(rate_limiter.calls)}")
        if api_key == settings.DEMO_API_KEY:
            if rate_limiter.is_rate_limited(formatted_ip):
                """logger.error(
                    f"Error while handling request. request_id={request_id} "
                    f"request_path={request.url.path}"
                    f"status code={429}"
                    f"code={error.to_code()}"
                    f"message={error.to_message()}",
                    exc_info=is_exc_info
                )"""
                raise RateLimitExceededAPIError(
                    "demo-api-key supports only 5 reqs per hour"
                )
        try:
            logger.info(
                f"REQUEST STARTED "
                f"request_id={request_id} "
                f"request_path={request.url.path} "
                f"ip={ip_address} "
                f"country={country} "
            )
            before = time.time()
            response: Response = await call_next(request)

            duration = time.time() - before
            process_time = (time.time() - before) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            if response.status_code != 404:
                logger.info(
                    f"REQUEST COMPLETED "
                    f"request_id={request_id} "
                    f"request_path={request.url.path} "
                    f"completed_in={formatted_process_time}ms "
                    f"status_code={response.status_code}"
                )
            return await _get_response_with_headers(response, duration)
        except Exception as error:
            if isinstance(error, APIErrorResponse):
                is_exc_info = error.to_status_code() == 500
                logger.error(
                    f"Error while handling request. request_id={request_id} "
                    f"request_path={request.url.path}"
                    f"status code={error.to_status_code()}"
                    f"code={error.to_code()}"
                    f"message={error.to_message()}",
                    exc_info=is_exc_info,
                )
            else:
                logger.error(
                    f"Error while handling request. request_id={request_id} "
                    f"request_path={request.url.path}",
                    exc_info=True,
                )
            raise error


async def _get_response_with_headers(response, duration):
    response = await add_response_headers(response, duration)
    return response
