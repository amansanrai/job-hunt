# Deployment and Activation Checklist

Use this after the code is pushed to GitHub. The automation will not send Airtable or Telegram updates until the secrets below are configured.

## 1. Enable GitHub Actions

Go to your repository on GitHub:

```text
Repository → Actions → Enable workflows
```

## 2. Add GitHub Actions secrets

Go to:

```text
Repository → Settings → Secrets and variables → Actions → New repository secret
```

Add these required secrets:

| Secret | Purpose |
| --- | --- |
| `AIRTABLE_API_KEY` | Airtable personal access token. `AIRTABLE_TOKEN` is also supported for backward compatibility. |
| `AIRTABLE_BASE_ID` | Airtable base id for the `Job System` base. |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather. |
| `TELEGRAM_CHAT_ID` | Your personal chat id or group chat id. |

Optional secret:

| Secret | Purpose |
| --- | --- |
| `NVIDIA_API_KEY` | Enables NVIDIA NIM cover-letter generation. Without this, the safe local fallback is used. |
| `ADZUNA_APP_ID` | Enables Adzuna API job sourcing. |
| `ADZUNA_APP_KEY` | Enables Adzuna API job sourcing. |

## 3. Get Telegram credentials

1. Open Telegram and message `BotFather`.
2. Run `/newbot` and copy the bot token into `TELEGRAM_BOT_TOKEN`.
3. Send `hello` to your bot.
4. Open this URL in a browser, replacing the token:

```text
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

5. Copy the numeric value at `message.chat.id` into `TELEGRAM_CHAT_ID`.

## 4. Create the Airtable token

Go to:

```text
https://airtable.com/create/tokens
```

Create a token with:

- `data.records:read`
- `data.records:write`
- `schema.bases:read`

Limit access to your `Job System` base.

## 5. Run activation check first

In GitHub:

```text
Actions → Career OS → Run workflow → mode: doctor, dry_run: true
```

The `doctor` mode prints which secrets are configured and whether NVIDIA is active.

## 6. Run the skill engine

```text
Actions → Career OS → Run workflow → mode: skills, dry_run: false
```

Expected result:

- one Airtable record in `Daily Tasks`
- one Telegram message with a 30-minute proof-of-work task

## 7. Run the job engine

```text
Actions → Career OS → Run workflow → mode: jobs, dry_run: false
```

Expected result:

- direct apply/review links in Airtable `Applications`
- generated draft files in the workflow artifact named `generated-resume-cover-letter-drafts`
- Telegram message with role, score, category, direct link, and draft name

## 8. If job extraction is empty

This is common during the first week if API credentials are missing or chosen ATS boards do not publish matching entry-level roles.

Do this:

1. Find a real job/application URL manually.
2. Add it to `data/seed_jobs.json`.
3. Commit and push.
4. Run `mode: jobs` again.

Example:

```json
{
  "jobs": [
    {
      "company": "Example Aerospace",
      "role": "UAV Design Intern",
      "category": "UAV",
      "location": "Bangalore",
      "link": "https://example.com/jobs/uav-design-intern/apply",
      "notes": "Direct apply link found manually; requires SolidWorks and aerodynamics basics."
    }
  ]
}
```

The system will score the seeded link, generate drafts, update Airtable, and notify Telegram.

## 9. Important safety rule

Do not add Selenium, Playwright, auto-submit, CAPTCHA bypass, or mass LinkedIn Easy Apply until the basic loop is stable:

```text
direct job link → Airtable → Telegram → human review → manual submit
```

## 10. Troubleshooting current common failures

### Airtable `HTTP 403: Forbidden`

This means the token is valid enough to reach Airtable, but Airtable is refusing access. Check all of these:

- the token has `data.records:write`
- the token has access to the exact `Job System` base
- `AIRTABLE_BASE_ID` starts with `app` and matches the base URL
- the target table exists: `Applications` for jobs, `Daily Tasks` for skills

The workflow now logs Airtable write failures and continues to Telegram so you still get the daily/job notification while fixing permissions.

### NVIDIA timeout

NVIDIA NIM can occasionally time out from GitHub-hosted runners. If that happens, the workflow uses the local truthful cover-letter fallback instead of failing the job run.

### Old failed runs still show old code

If a failed log checks out an older commit SHA, rerun the workflow after merging/pushing the latest branch. Older logs may still show fatal Airtable/NVIDIA exceptions from before the nonfatal external-API handling was added.

### Airtable `HTTP 422: Unprocessable Entity`

This usually means Airtable accepted the token but rejected the record shape. Common causes are missing fields, incompatible field types, or missing single-select options. The client sends `typecast: true` to help Airtable coerce select/number/date values, but it cannot create missing fields. Confirm the tables still contain the fields listed in `docs/setup.md`.
