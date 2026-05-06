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
Actions → Career OS → Run workflow → mode: doctor
```

The `doctor` mode prints which secrets are configured and whether NVIDIA is active.

## 6. Run the skill engine

```text
Actions → Career OS → Run workflow → mode: skills
```

Expected result:

- one Airtable record in `Daily Tasks`
- one Telegram message with a 30-minute proof-of-work task

## 7. Run the job engine

```text
Actions → Career OS → Run workflow → mode: jobs
```

Expected result:

- direct apply/review links in Airtable `Applications`
- generated draft files in the workflow artifact named `generated-resume-cover-letter-drafts`
- Telegram message with role, score, category, direct link, and draft name

## 8. If job extraction is empty

This is common during the first week because some career sites block automated requests or hide jobs behind JavaScript.

Do this instead of accepting random company homepages:

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
