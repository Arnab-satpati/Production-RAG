from __future__ import annotations

import time
from collections import defaultdict
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from rag.config.settings import get_settings

if TYPE_CHECKING:
    from starlette.requests import Request


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int | None = None) -> None:
        super().__init__(app)
        self._rpm = requests_per_minute or get_settings().guardrails.rate_limit_per_minute
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60

        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= self._rpm:
            retry_after = 60 - (now - self._requests[client_ip][0])
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": round(retry_after, 1),
                },
                headers={"Retry-After": str(int(retry_after))},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
