import httpx

from noa_finder._http import RetryTransport


def _client_with_retry(handler, **kwargs):
    transport = RetryTransport(
        httpx.MockTransport(handler),
        backoff=0.001,
        sleep=kwargs.pop("sleep", lambda _s: None),
        **kwargs,
    )
    return httpx.Client(base_url="https://x", transport=transport)


def test_retries_on_429_then_succeeds():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    sleeps: list[float] = []
    client = _client_with_retry(handler, sleep=sleeps.append)
    r = client.get("/anything")
    assert r.status_code == 200
    assert calls["n"] == 3
    assert len(sleeps) == 2


def test_retries_on_503_then_gives_up():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    client = _client_with_retry(handler, max_retries=2)
    r = client.get("/anything")
    assert r.status_code == 503


def test_passes_through_2xx_without_retry():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={})

    client = _client_with_retry(handler)
    assert client.get("/x").status_code == 200
    assert calls["n"] == 1


def test_does_not_retry_4xx_other_than_429():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404)

    client = _client_with_retry(handler)
    assert client.get("/x").status_code == 404
    assert calls["n"] == 1


def test_honors_retry_after_seconds_floor():
    def handler(request: httpx.Request) -> httpx.Response:
        return (
            httpx.Response(429, headers={"Retry-After": "5"})
            if not handler.done  # type: ignore[attr-defined]
            else httpx.Response(200)
        )

    handler.done = False  # type: ignore[attr-defined]

    sleeps: list[float] = []

    def sleep(s: float) -> None:
        sleeps.append(s)
        handler.done = True  # type: ignore[attr-defined]

    client = _client_with_retry(handler, sleep=sleep)
    r = client.get("/x")
    assert r.status_code == 200
    assert sleeps == [5.0]
