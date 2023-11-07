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
    usage: Dict = repo.get_usage_by_user(user.uid, None)
    usage_response: UsageStatistics = UsageStatistics.from_usage_dict(usage)
    return GetUserResponse.from_user(user, [usage_response])
