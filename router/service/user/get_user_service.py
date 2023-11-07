from datetime import datetime
from datetime import timedelta
from typing import Dict

from router.domain.user.entities import User
from router.repository.token_usage_repository import TokenUsageRepositoryFirestore
from router.repository.user_repository import UserRepositoryFirebase
from router.service import error_responses
from router.service.user.entities import GetUserResponse
from router.service.user.entities import UsageStatistics


def execute(user_uid: str, user_repository: UserRepositoryFirebase) -> GetUserResponse:
    user: User = user_repository.get_user(user_uid)
    if not user:
        raise error_responses.NotFoundAPIError("user")
    repo: TokenUsageRepositoryFirestore = TokenUsageRepositoryFirestore.instance()
    # At some point when we have multiple models specify model too?
    subscription_period_start: int = _get_subscription_current_period_start(user.created_at)
    usage: Dict = repo.get_usage_by_user(user.uid, None, subscription_period_start)
    usage_response: UsageStatistics = UsageStatistics.from_usage_dict(usage)
    return GetUserResponse.from_user(user, [usage_response])


def _get_subscription_current_period_start(registration_ts: int) -> int:
    """
    Returns latest period that is less than 30 days from created_at timestamp
    """
    current_timestamp = int(datetime.utcnow().timestamp())
    if current_timestamp < registration_ts:
        return current_timestamp - (24 * 30 * 60 * 60)
    datetime_object = datetime.fromtimestamp(registration_ts)

    # Add 30 days repeatedly until datetime_object is within 30 days of the current time
    while (datetime.fromtimestamp(current_timestamp) - datetime_object).days > 30:
        datetime_object += timedelta(days=30)
    final_timestamp = datetime_object.timestamp()
    return int(final_timestamp)
