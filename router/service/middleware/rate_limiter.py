import time
from collections import defaultdict

from router.repository.demo_user_repository import DemoUserRepositoryFirebase


class RateLimiter:
    def __init__(
        self, max_calls_per_hour, usage_repository: DemoUserRepositoryFirebase
    ):
        self.calls = defaultdict(list)
        self.max_calls_per_hour = max_calls_per_hour
        self.usage_repository = usage_repository

    def is_rate_limited(self, formatted_ip: str):
        count = self.usage_repository.get_last_hour_usage_count(ip_address=formatted_ip)
        if count <= self.max_calls_per_hour:
            self.usage_repository.track_usage(formatted_ip)
            return False
        return True

    def is_rate_limited_old(self, s):
        now = time.time()
        one_hour_ago = now - 3600
        self.calls[s] = [t for t in self.calls[s] if t > one_hour_ago]
        self.calls[s].append(now)
        return len(self.calls[s]) > self.max_calls_per_hour
