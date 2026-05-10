from __future__ import annotations

from typing import Any, Iterator

import httpx

from ._http import default_transport

CONTRACT_CODES = ["A", "B", "C", "D"]
GRANT_CODES = ["02", "03", "04", "05"]
LOAN_CODES = ["07", "08"]
DIRECT_PAYMENT_CODES = ["06", "10"]
OTHER_CODES = ["09", "11"]
ALL_AWARD_TYPE_CODES = (
    CONTRACT_CODES + GRANT_CODES + LOAN_CODES + DIRECT_PAYMENT_CODES + OTHER_CODES
)

AWARD_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Start Date",
    "End Date",
    "Award Amount",
    "Total Outlays",
    "Description",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Award Type",
    "generated_internal_id",
]


class USASpendingClient:
    def __init__(
        self,
        base_url: str = "https://api.usaspending.gov/api/v2",
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport if transport is not None else default_transport(),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "USASpendingClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def search_awards_by_uei(self, uei: str, page_size: int = 100) -> Iterator[dict[str, Any]]:
        page = 1
        while True:
            body = {
                "filters": {
                    "recipient_search_text": [uei],
                    "award_type_codes": ALL_AWARD_TYPE_CODES,
                },
                "fields": AWARD_FIELDS,
                "page": page,
                "limit": page_size,
                "sort": "Award Amount",
                "order": "desc",
            }
            r = self._http.post("/search/spending_by_award/", json=body)
            r.raise_for_status()
            payload = r.json()
            results = payload.get("results") or []
            for row in results:
                yield row
            metadata = payload.get("page_metadata") or {}
            has_next = metadata.get("hasNext")
            if has_next is None:
                has_next = len(results) >= page_size
            if not has_next:
                return
            page += 1
