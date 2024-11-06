import asyncio
from datetime import datetime

class RateLimiter:
    def __init__(self, calls_per_second: int):
        self.calls_per_second = calls_per_second
        self.last_call_time = datetime.now()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current_time = datetime.now()
            time_since_last_call = (current_time - self.last_call_time).total_seconds()
            if time_since_last_call < 1.0 / self.calls_per_second:
                await asyncio.sleep(1.0 / self.calls_per_second - time_since_last_call)
            self.last_call_time = datetime.now()