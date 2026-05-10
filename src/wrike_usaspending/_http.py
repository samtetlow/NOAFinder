from __future__ import annotations

import time
from typing import Callable

import httpx

DEFAULT_RETRY_STATUSES: tuple[int, ...] = (429, 500, 502, 503, 504)


class RetryTransport(httpx.BaseTransport):
    def __init__(
        self,
        wrapped: httpx.BaseTransport,
        *,
        max_retries: int = 4,
        retry_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
        backoff: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._wrapped = wrapped
        self._max_retries = max_retries
        self._retry_statuses = retry_statuses
        self._backoff = backoff
        self._sleep = sleep

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        attempt = 0
        while True:
            response = self._wrapped.handle_request(request)
            if (
                response.status_code not in self._retry_statuses
                or attempt >= self._max_retries
            ):
                return response
            response.read()
            response.close()
            sleep_for = self._backoff * (2**attempt)
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_for = max(sleep_for, float(retry_after))
                except ValueError:
                    pass
            self._sleep(sleep_for)
            attempt += 1


def default_transport() -> httpx.BaseTransport:
    return RetryTransport(httpx.HTTPTransport())
