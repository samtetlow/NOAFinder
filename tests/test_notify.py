import json
from datetime import datetime, timezone

import httpx
import pytest

from noa_finder.digest import build_digest
from noa_finder.notify import EmailNotifier, SlackNotifier, send_digest


def _empty_digest():
    return build_digest([], now=datetime(2026, 5, 4, 13, 0, tzinfo=timezone.utc))


def _digest_with_awards():
    results = [{
        "task_id": "T1", "task_title": "Acme", "uei": "U", "skipped": False,
        "reason": None, "awards_found": 1, "subtasks_created": 1,
        "subtasks_skipped_existing": 0, "subtasks_skipped_no_id": 0,
        "created_awards": [{
            "award_id": "X-1", "title": "Acme", "total_amount": 100.0,
            "outlay_amount": 50.0, "awarding_agency": "DOD",
            "award_type": "Contract", "generated_internal_id": "CAW",
            "url": "https://www.usaspending.gov/award/CAW/",
        }],
        "dry_run": False,
    }]
    return build_digest(results, now=datetime(2026, 5, 4, 13, 0, tzinfo=timezone.utc))


def test_slack_notifier_posts_text_and_blocks():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(200, text="ok")

    notifier = SlackNotifier(
        "https://hooks.slack.com/services/AAA/BBB",
        transport=httpx.MockTransport(handler),
    )
    try:
        notifier.send("hello", blocks=[{"type": "section"}])
    finally:
        notifier.close()

    assert captured["url"] == "https://hooks.slack.com/services/AAA/BBB"
    assert captured["body"]["text"] == "hello"
    assert captured["body"]["blocks"] == [{"type": "section"}]


def test_slack_notifier_raises_on_non_2xx():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="invalid_payload")

    notifier = SlackNotifier(
        "https://hooks.slack.com/x", transport=httpx.MockTransport(handler)
    )
    try:
        with pytest.raises(httpx.HTTPStatusError):
            notifier.send("hi")
    finally:
        notifier.close()


class _FakeSMTP:
    last_instance: "_FakeSMTP | None" = None

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.calls: list[tuple] = []
        _FakeSMTP.last_instance = self

    def starttls(self):
        self.calls.append(("starttls",))

    def login(self, username, password):
        self.calls.append(("login", username, password))

    def send_message(self, msg):
        self.calls.append(("send_message", msg))

    def quit(self):
        self.calls.append(("quit",))


class _FakeSMTPSSL(_FakeSMTP):
    pass


def test_email_notifier_sends_text_and_html():
    notifier = EmailNotifier(
        host="mail.example.com", port=587,
        username="u", password="p",
        from_addr="me@example.com", to_addrs=["a@example.com", "b@example.com"],
        smtp_factory=_FakeSMTP,
    )
    notifier.send("subj", text_body="plain", html_body="<b>html</b>")

    smtp = _FakeSMTP.last_instance
    assert smtp is not None
    actions = [c[0] for c in smtp.calls]
    assert actions == ["starttls", "login", "send_message", "quit"]
    msg = smtp.calls[2][1]
    assert msg["Subject"] == "subj"
    assert msg["From"] == "me@example.com"
    assert "a@example.com" in msg["To"]
    assert "b@example.com" in msg["To"]
    assert msg.is_multipart()
    payloads = [p.get_content_type() for p in msg.iter_parts()]
    assert "text/plain" in payloads
    assert "text/html" in payloads


def test_email_notifier_skips_login_when_no_username():
    notifier = EmailNotifier(
        host="mail.example.com", port=587,
        username=None, password=None,
        from_addr="me@example.com", to_addrs=["a@example.com"],
        smtp_factory=_FakeSMTP,
    )
    notifier.send("s", "t")
    actions = [c[0] for c in _FakeSMTP.last_instance.calls]
    assert "login" not in actions


def test_email_notifier_skips_starttls_when_disabled():
    notifier = EmailNotifier(
        host="mail.example.com", port=587,
        username=None, password=None,
        from_addr="me@example.com", to_addrs=["a@example.com"],
        use_tls=False,
        smtp_factory=_FakeSMTP,
    )
    notifier.send("s", "t")
    actions = [c[0] for c in _FakeSMTP.last_instance.calls]
    assert "starttls" not in actions


def test_email_notifier_uses_smtp_ssl_for_port_465():
    notifier = EmailNotifier(
        host="mail.example.com", port=465,
        username="u", password="p",
        from_addr="me@example.com", to_addrs=["a@example.com"],
        smtp_factory=_FakeSMTP, smtp_ssl_factory=_FakeSMTPSSL,
    )
    notifier.send("s", "t")
    smtp = _FakeSMTP.last_instance
    assert isinstance(smtp, _FakeSMTPSSL)
    actions = [c[0] for c in smtp.calls]
    assert "starttls" not in actions
    assert "login" in actions


def test_email_notifier_requires_recipients():
    with pytest.raises(ValueError):
        EmailNotifier(
            host="x", port=587, username=None, password=None,
            from_addr="me@example.com", to_addrs=[],
        )


def test_send_digest_skips_when_empty_and_notify_off():
    digest = _empty_digest()

    class _StubSlack:
        sent = False
        def send(self, *a, **kw): self.sent = True

    s = _StubSlack()
    report = send_digest(digest, slack=s, email=None, notify_on_empty=False)
    assert report == {"slack_sent": False, "email_sent": False, "skipped_empty": True}
    assert s.sent is False


def test_send_digest_sends_when_notify_on_empty_true():
    digest = _empty_digest()

    class _StubSlack:
        last = None
        def send(self, text, blocks=None):
            self.last = (text, blocks)

    s = _StubSlack()
    report = send_digest(digest, slack=s, email=None, notify_on_empty=True)
    assert report["slack_sent"] is True
    assert s.last is not None


def test_send_digest_skips_channels_when_notifier_is_none():
    digest = _digest_with_awards()
    report = send_digest(digest, slack=None, email=None, notify_on_empty=True)
    assert report["slack_sent"] is False
    assert report["email_sent"] is False


def test_send_digest_only_email_when_slack_unset():
    digest = _digest_with_awards()

    class _StubEmail:
        last = None
        def send(self, *, subject, text_body, html_body=None):
            self.last = (subject, text_body, html_body)

    e = _StubEmail()
    report = send_digest(digest, slack=None, email=e, notify_on_empty=True)
    assert report["email_sent"] is True
    assert report["slack_sent"] is False
    assert e.last is not None
