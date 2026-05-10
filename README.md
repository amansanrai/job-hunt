# Job Hunt Career OS

Free GitHub Actions automation for an India-focused aerospace job hunt.

This repo implements a conservative workflow: the system finds relevant roles, scores them, drafts truthful resume/cover-letter material, updates Airtable, and sends Telegram alerts. It does **not** auto-submit applications, so the final review and submit step stays human-controlled.

## What runs automatically

The workflow in `.github/workflows/career-os.yml` runs four times per day and can also be triggered manually.

Pipeline modules:

1. **Job Finder** — checks configured aerospace, drone, defense, and supplier career pages.
2. **Match Scoring** — scores roles for UAV, CFD, CAD, simulation, rocketry, aerospace manufacturing, and documentation fit.
3. **Resume Drafting** — creates DOCX drafts from the truthful master profile and the role category.
4. **Cover Letter Drafting** — uses NVIDIA NIM when `NVIDIA_API_KEY` is set; otherwise it uses a safe local template.
5. **Airtable Update** — creates records in the `Applications` and `Daily Tasks` tables.
6. **Telegram Update** — sends direct review/apply links, match scores, and the daily skill task.
7. **Skill Engine** — chooses a 30-minute proof-of-work task based on repeated skill gaps.

## Repository structure

```text
.github/workflows/career-os.yml   # scheduled GitHub Actions runner
src/career_os/                    # Python automation engine
data/master_profile.json          # single source of truth for the candidate profile
data/sources.json                 # free job source configuration and keywords
data/seed_jobs.json               # optional manually verified direct apply links
docs/setup.md                     # Airtable, Telegram, NVIDIA, and manual-run setup
```

## Free services used

| Purpose | Tool |
| --- | --- |
| Scheduler | GitHub Actions |
| Database/dashboard | Airtable |
| Notifications | Telegram bot |
| AI text generation | NVIDIA NIM API, optional |
| Resume drafts | Python DOCX generation |
| Artifact storage | GitHub Actions artifacts |

## Quick start

The runtime uses only the Python standard library; no paid services or server are required.

1. Create the Airtable schema in [`docs/setup.md`](docs/setup.md).
2. Add GitHub secrets for Airtable, Telegram, and optionally NVIDIA.
3. Update [`data/master_profile.json`](data/master_profile.json) with your real CV details.
4. Update [`data/sources.json`](data/sources.json) if you want to add or remove career pages.
5. Follow the deployment checklist in [`docs/deployment.md`](docs/deployment.md).
6. Run locally in dry-run mode:

```bash
PYTHONPATH=src DRY_RUN=true python -m career_os.main --mode all
```

### Safe try-first branch workflow

1. Create a branch for the experiment.
2. Make one focused change.
3. Run local dry-run and tests.
4. Run GitHub Actions manually with `dry_run: true`.
5. Review logs/artifacts, then merge only after results are stable.

## Safety rules

- The workflow only prepares drafts and tracking records.
- The job finder rejects plain homepages and generic career landing pages unless explicitly allowed; use `data/seed_jobs.json` for verified direct apply links when a site blocks scraping.
- It does not bypass CAPTCHA, auto-submit forms, or spam job boards.
- Resume generation must stay truthful: it reorders and emphasizes existing profile evidence, but does not invent experience.
- Career pages are checked at low frequency to avoid aggressive scraping.
