from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any, Callable, Sequence

import httpx

from ._http import default_transport
from .digest import DigestPayload


class SlackNotifier:
    def __init__(
        self,
        webhook_url: str,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._webhook_url = webhook_url
        self._http = httpx.Client(
            timeout=timeout,
            transport=transport if transport is not None else default_transport(),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SlackNotifier":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def send(self, text: str, blocks: list[dict[str, Any]] | None = None) -> None:
        body: dict[str, Any] = {"text": text}
        if blocks:
            body["blocks"] = blocks
        r = self._http.post(self._webhook_url, json=body)
        r.raise_for_status()


class EmailNotifier:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        username: str | None,
        password: str | None,
        from_addr: str,
        to_addrs: Sequence[str],
        use_tls: bool = True,
        smtp_factory: Callable[..., smtplib.SMTP] | None = None,
        smtp_ssl_factory: Callable[..., smtplib.SMTP_SSL] | None = None,
    ) -> None:
        if not to_addrs:
            raise ValueError("EmailNotifier requires at least one recipient")
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_addr = from_addr
        self._to_addrs = list(to_addrs)
        self._use_tls = use_tls
        self._smtp_factory = smtp_factory or smtplib.SMTP
        self._smtp_ssl_factory = smtp_ssl_factory or smtplib.SMTP_SSL

    def send(self, subject: str, text_body: str, html_body: str | None = None) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)
        msg.set_content(text_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        if self._port == 465:
            client = self._smtp_ssl_factory(self._host, self._port)
        else:
            client = self._smtp_factory(self._host, self._port)

        try:
            if self._port != 465 and self._use_tls:
                client.starttls()
            if self._username:
                client.login(self._username, self._password or "")
            client.send_message(msg)
        finally:
            try:
                client.quit()
            except Exception:
                pass


def send_digest(
    digest: DigestPayload,
    *,
    slack: SlackNotifier | None,
    email: EmailNotifier | None,
    notify_on_empty: bool = True,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "slack_sent": False,
        "email_sent": False,
        "skipped_empty": False,
    }

    if digest.total_new_subtasks == 0 and not notify_on_empty:
        report["skipped_empty"] = True
        return report

    if slack is not None:
        slack.send(digest.slack_text, blocks=digest.slack_blocks)
        report["slack_sent"] = True

    if email is not None:
        email.send(
            subject=digest.email_subject,
            text_body=digest.email_text,
            html_body=digest.email_html,
        )
        report["email_sent"] = True

    return report
