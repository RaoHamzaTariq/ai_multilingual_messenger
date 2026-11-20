import time
from typing import Dict, List

class UserRateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._user_requests: Dict[str, List[float]] = {}

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        timestamps = self._user_requests.setdefault(user_id, [])

        # Remove timestamps older than the window
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        self._user_requests[user_id] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            return False

        self._user_requests[user_id].append(now)
        return True

# Shared default limiter (30 requests per minute per user)
rate_limiter = UserRateLimiter(max_requests=30, window_seconds=60)
