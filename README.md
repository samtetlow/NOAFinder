# NOA Finder

A weekly Notice-of-Award radar for **Grant Engine**.

NOA Finder reads a recipient **UEI** (Unique Entity Identifier) custom field
off Wrike tasks, queries [USASpending.gov](https://api.usaspending.gov/) for
every federal award tied to that UEI, writes one **subtask per award** back
into Wrike, and (via the `weekly-digest` subcommand) sends a Slack + email
roll-up of any awards added during the run.

Per-award subtask captures:

- Project / recipient title
- Award date (period of performance start)
- Total award amount
- Grant / contract tracking number (Award ID)
- Amount pulled down (total outlays)
- Description / abstract
- Awarding agency and award type

Subtasks are created under the parent task, giving you a built-in "table"
view in Wrike (parent task → child rows). Re-running the sync is
idempotent: existing subtasks for the same Award ID are skipped.

## How it fits together

```
GH Actions cron ─► noa-finder weekly-digest ─► Wrike (read UEIs, write new subtasks)
                                          └► USASpending.gov (search awards)
                                          └► Slack webhook + SMTP (digest)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# paste your WRIKE_TOKEN, plus Slack webhook + SMTP creds for the digest
```

Get a Wrike permanent token from **Profile → Apps & Integrations → API**.

## Usage

Discover the ID of your `uei` custom field:

```bash
noa-finder list-custom-fields
```

List your Wrike spaces (to find the space ID for `sync-space` /
`weekly-digest`):

```bash
noa-finder list-spaces
```

Sync every task across an entire Wrike space:

```bash
noa-finder sync-space <SPACE_ID>
```

Other sync entry points:

```bash
noa-finder sync-folder <FOLDER_ID>
noa-finder sync-task   <TASK_ID>
```

Add `--dry-run` to any sync command to preview without creating subtasks.

### Weekly digest (Slack + email)

```bash
noa-finder weekly-digest <SPACE_ID> --no-send   # preview the digest body
noa-finder weekly-digest <SPACE_ID>              # real run, sends Slack + email
```

Flags:

- `--dry-run` — skip creating Wrike subtasks but still build/send the digest
- `--no-send` — build the digest and print it to stdout, don't POST/SMTP
- `--no-slack`, `--no-email` — disable a single channel for this run

The digest groups newly created subtasks by Wrike parent task and includes
the recipient name, total amount, outlays, awarding agency, and a link to
the USASpending.gov award page (when USASpending returned a
`generated_internal_id`). Slack messages are capped at 25 tasks with an
overflow note pointing to the email, which has no practical size limit.

## Running on GitHub Actions (recommended)

`.github/workflows/weekly-digest.yml` is included. To enable:

1. **Repo Settings → Secrets and variables → Actions → Secrets → New
   repository secret:**

   | Secret | Value |
   |---|---|
   | `WRIKE_TOKEN` | Wrike permanent access token |
   | `WRIKE_SPACE_ID` | Wrike space holding client tasks |
   | `SLACK_WEBHOOK_URL` | Slack incoming webhook URL ([create one](https://api.slack.com/messaging/webhooks)) |
   | `SMTP_HOST` | e.g. `smtp.gmail.com`, `email-smtp.us-east-1.amazonaws.com`, `smtp.postmarkapp.com` |
   | `SMTP_USERNAME` | SMTP user / API key id |
   | `SMTP_PASSWORD` | SMTP password / app password / API secret |
   | `EMAIL_FROM` | `noa@yourdomain.com` |
   | `EMAIL_TO` | comma-separated recipients |

2. **Repo Settings → Variables** (non-sensitive, optional overrides):
   `WRIKE_UEI_FIELD_NAME`, `SMTP_PORT` (default `587`), `SMTP_USE_TLS`
   (default `true`), `DIGEST_TIMEZONE` (default `America/New_York`),
   `DIGEST_SEND_WHEN_EMPTY` (default `true`).

3. **Actions tab → "Weekly NOA digest" → Run workflow** to verify
   end-to-end. Once that succeeds, the Monday cron takes over.

The schedule is fixed UTC (`0 13 * * 1`); that's 9 AM ET in summer (EDT)
and 8 AM ET in winter (EST). Edit the cron line in the workflow file if
you want different timing. Job failures email the workflow owner via
GitHub's built-in notifications.

### SMTP recipes

- **Gmail**: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`,
  `SMTP_USE_TLS=true`. Generate an app password.
- **Amazon SES**: `SMTP_HOST=email-smtp.<region>.amazonaws.com`,
  `SMTP_PORT=587`. Username + password come from SES SMTP credentials.
- **Postmark**: `SMTP_HOST=smtp.postmarkapp.com`, `SMTP_PORT=587`. The
  username and password are both your Postmark server token.

## What gets written into Wrike

For each award returned by USASpending, a subtask is created under the
parent task:

- **Title**: `[USASpending] <AWARD_ID> — $<TOTAL>`
- **Description** (HTML, rendered as a table by Wrike): Project Title,
  Award / Contract / Grant #, Award Date, Total Award Amount, Amount
  Pulled Down (Outlays), Award Type, Awarding Agency, full
  description/abstract.

Each subtask also has its Award ID stored in a Wrike text custom field
called **`USASpending Award ID`**. NOA Finder auto-creates this field on
first run if it doesn't exist, and uses it (preferred) plus the title
prefix (fallback) to detect already-imported awards on subsequent runs.

## Tests

```bash
pytest
```

## Notes & assumptions

- The UEI is read from a Wrike *task-level* custom field whose title
  matches `WRIKE_UEI_FIELD_NAME` (default: `uei`, case-insensitive).
- USASpending is queried with `recipient_search_text=[uei]` across
  contract, grant, loan, direct payment, and other-financial award type
  codes.
- "Amount pulled down" maps to USASpending's `Total Outlays` (cumulative
  disbursements).
- Subtasks are created in the parent task's first folder.
- "New this week" === "newly created on this run". If a manual run
  between cron triggers absorbs new awards, the next weekly digest will
  under-report — acceptable for the small-team use case.
- App-level failure alerts are intentionally not implemented; GitHub
  Actions sends job-failure email to the workflow owner.
