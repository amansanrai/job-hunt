# Career OS Setup

## 1. Airtable tables

Create a base named `Job System` with these tables.

### Applications

Required fields:

- `Company` — single line text
- `Role` — single line text
- `Category` — single select: Rocketry, UAV, CFD, Simulation, CAD, Aerospace Manufacturing, Aircraft Documentation
- `Location` — single line text
- `Link` — URL
- `Status` — single select: Pending, Applied, Rejected, Interview
- `Match Score` — number
- `Resume Used` — single line text
- `Cover Letter` — single line text
- `Applied` — checkbox
- `Date` — date
- `Notes` — long text

### Daily Tasks

Required fields:

- `Date` — date
- `Skill` — single line text
- `Category` — single line text
- `Task` — long text
- `Difficulty` — single line text
- `Completed` — checkbox
- `Resource` — URL
- `Notes` — long text

### Skills

Recommended fields: `Skill`, `Category`, `Priority`, `Progress`, `Last Practiced`, `Resource`, `Notes`.

### Resume Versions

Recommended fields: `Resume Name`, `Role Type`, `Link`, `Last Updated`, `Notes`.

## 2. GitHub secrets

Add these repository secrets:

- `AIRTABLE_TOKEN`
- `AIRTABLE_BASE_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `NVIDIA_API_KEY` (optional; fallback templates work without it)

## 3. GitHub variables

Optional variables:

- `AIRTABLE_APPLICATIONS_TABLE` (default: `Applications`)
- `AIRTABLE_DAILY_TASKS_TABLE` (default: `Daily Tasks`)
- `AIRTABLE_SKILLS_TABLE` (default: `Skills`)
- `AIRTABLE_RESUME_VERSIONS_TABLE` (default: `Resume Versions`)
- `NVIDIA_MODEL` (default: `meta/llama-3.1-70b-instruct`)

## 4. Manual run

```bash
PYTHONPATH=src DRY_RUN=true python -m career_os.main --mode all
```

`DRY_RUN=true` logs Airtable and Telegram writes instead of sending them.
