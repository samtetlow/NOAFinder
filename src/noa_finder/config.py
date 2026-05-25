from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    wrike_token: str
    wrike_base_url: str
    wrike_uei_field_name: str
    wrike_program_manager_field_name: str | None
    wrike_grant_number_field_name: str | None
    wrike_project_title_field_name: str | None
    usaspending_base_url: str
    request_timeout: float


@dataclass(frozen=True)
class NotifyConfig:
    slack_webhook_url: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_use_tls: bool
    email_from: str | None
    email_to: tuple[str, ...]
    digest_timezone: str
    digest_send_when_empty: bool

    @property
    def slack_enabled(self) -> bool:
        return bool(self.slack_webhook_url)

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_host and self.email_from and self.email_to)


def load_config() -> Config:
    load_dotenv()
    token = os.environ.get("WRIKE_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "WRIKE_TOKEN env var is required. Create a permanent token in "
            "Wrike: Profile -> Apps & Integrations -> API."
        )
    return Config(
        wrike_token=token,
        wrike_base_url=os.environ.get(
            "WRIKE_BASE_URL", "https://www.wrike.com/api/v4"
        ).rstrip("/"),
        wrike_uei_field_name=os.environ.get("WRIKE_UEI_FIELD_NAME", "uei"),
        wrike_program_manager_field_name=os.environ.get(
            "WRIKE_PM_FIELD_NAME", ""
        ).strip() or None,
        wrike_grant_number_field_name=os.environ.get(
            "WRIKE_GRANT_NUMBER_FIELD_NAME", ""
        ).strip() or None,
        wrike_project_title_field_name=os.environ.get(
            "WRIKE_PROJECT_TITLE_FIELD_NAME", ""
        ).strip() or None,
        usaspending_base_url=os.environ.get(
            "USASPENDING_BASE_URL", "https://api.usaspending.gov/api/v2"
        ).rstrip("/"),
        request_timeout=float(os.environ.get("REQUEST_TIMEOUT", "30")),
    )


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _bool(value: str, default: bool) -> bool:
    if value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_notify_config() -> NotifyConfig:
    load_dotenv()
    return NotifyConfig(
        slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL", "").strip() or None,
        smtp_host=os.environ.get("SMTP_HOST", "").strip() or None,
        smtp_port=int(os.environ.get("SMTP_PORT", "587")),
        smtp_username=os.environ.get("SMTP_USERNAME", "").strip() or None,
        smtp_password=os.environ.get("SMTP_PASSWORD") or None,
        smtp_use_tls=_bool(os.environ.get("SMTP_USE_TLS", ""), True),
        email_from=os.environ.get("EMAIL_FROM", "").strip() or None,
        email_to=_split_csv(os.environ.get("EMAIL_TO", "")),
        digest_timezone=os.environ.get("DIGEST_TIMEZONE", "America/New_York"),
        digest_send_when_empty=_bool(
            os.environ.get("DIGEST_SEND_WHEN_EMPTY", ""), True
        ),
    )
