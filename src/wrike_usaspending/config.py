from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    wrike_token: str
    wrike_base_url: str
    wrike_uei_field_name: str
    usaspending_base_url: str
    request_timeout: float


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
        wrike_base_url=os.environ.get("WRIKE_BASE_URL", "https://www.wrike.com/api/v4").rstrip("/"),
        wrike_uei_field_name=os.environ.get("WRIKE_UEI_FIELD_NAME", "uei"),
        usaspending_base_url=os.environ.get(
            "USASPENDING_BASE_URL", "https://api.usaspending.gov/api/v2"
        ).rstrip("/"),
        request_timeout=float(os.environ.get("REQUEST_TIMEOUT", "30")),
    )
