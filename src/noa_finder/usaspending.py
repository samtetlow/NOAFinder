from __future__ import annotations

from typing import Any, Iterator

import httpx

from ._http import default_transport

# USASpending requires `award_type_codes` to come from a single group per
# request (per their /references/data_dictionary). To pull every award type
# for a recipient we have to issue one search per group and merge the results.
AWARD_TYPE_GROUPS: list[list[str]] = [
    ["A", "B", "C", "D"],         # contracts
    ["02", "03", "04", "05"],     # grants
    ["07", "08"],                 # loans
    ["06", "10"],                 # direct payments
    ["09", "11"],                 # other financial assistance
]

# Field list requested back from USASpending for each award. These names are
# valid for all 5 award_type_codes groups (contracts share the same Recipient
# Name / Award Amount / Total Outlays as grants).
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

    def _search_one_group(
        self,
        uei: str,
        award_type_codes: list[str],
        page_size: int,
    ) -> Iterator[dict[str, Any]]:
        # Sort is intentionally omitted. USASpending's sort field names differ
        # by award_type_codes group (e.g. "Award Amount" is valid for contracts
        # but rejected for some other groups with 400 "Sort value not found").
        # We re-sort client-side in report.build_report after merging groups.
        page = 1
        while True:
            body = {
                "filters": {
                    "recipient_search_text": [uei],
                    "award_type_codes": award_type_codes,
                },
                "fields": AWARD_FIELDS,
                "page": page,
                "limit": page_size,
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

    def search_awards_by_uei(
        self, uei: str, page_size: int = 100
    ) -> Iterator[dict[str, Any]]:
        for group in AWARD_TYPE_GROUPS:
            yield from self._search_one_group(uei, group, page_size)
