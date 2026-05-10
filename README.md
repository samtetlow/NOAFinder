# wrike-usaspending

Pulls a recipient **UEI** (Unique Entity Identifier) custom field off Wrike tasks,
queries [USASpending.gov](https://api.usaspending.gov/) for every federal award tied to that UEI,
and writes one **subtask per award** back into Wrike with the key fields:

- Project / recipient title
- Award date (period of performance start)
- Total award amount
- Grant / contract tracking number (Award ID)
- Amount pulled down (total outlays)
- Description / abstract
- Awarding agency and award type

Subtasks are created under the parent task, giving you a built-in "table" view in Wrike
(parent task → child rows). Re-running the sync is idempotent: existing subtasks for the
same Award ID are skipped.

## How it fits together

```
Wrike task ──(custom field "uei")──► USASpending.gov API ──► Wrike subtasks (one per award)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# edit .env to add your WRIKE_TOKEN
```

Get a Wrike permanent token from **Profile → Apps & Integrations → API**.

## Usage

Discover the ID of your "uei" custom field (and confirm the name matches):

```bash
wrike-usaspending list-custom-fields
```

Sync a single Wrike task by ID:

```bash
wrike-usaspending sync-task IEAA7BPMI4XXXXXX
```

Sync every task in a Wrike folder/project:

```bash
wrike-usaspending sync-folder IEAA7BPMI4XXXXXX
```

Add `--dry-run` to preview without creating subtasks.

Output is JSON with `awards_found`, `subtasks_created`, and `subtasks_skipped_existing`.

## What gets written into Wrike

For each award returned by USASpending, a subtask is created under the parent task:

- **Title**: `[USASpending] <AWARD_ID> — $<TOTAL>`
- **Description** (HTML, rendered as a small table by Wrike):
  - Project Title
  - Award / Contract / Grant #
  - Award Date
  - Total Award Amount
  - Amount Pulled Down (Outlays)
  - Award Type
  - Awarding Agency
  - Description / Abstract

The `[USASpending]` prefix and Award ID in the title are how the sync detects already-imported
awards on subsequent runs.

## Tests

```bash
pytest
```

## Notes & assumptions

- The UEI is read from a Wrike *task-level* custom field whose title matches `WRIKE_UEI_FIELD_NAME`
  (default: `uei`, case-insensitive).
- USASpending is queried with `recipient_search_text=[uei]` across contract, grant, loan,
  direct payment, and other-financial award type codes.
- "Amount pulled down" maps to USASpending's `Total Outlays` (cumulative disbursements).
- Subtasks are created in the parent task's first folder. If you want them in a dedicated
  reporting space, move/clone the parent task into that space before syncing.
