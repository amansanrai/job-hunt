from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .ai import generate_cover_letter
from .airtable_client import AirtableClient
from .config import ROOT, Settings, load_profile, load_sources
from .job_finder import find_jobs
from .resume import create_tailored_resume
from .skills import choose_daily_skill
from .telegram import send_telegram

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def run_jobs(settings: Settings) -> list[str]:
    profile = load_profile()
    sources = load_sources()
    jobs = find_jobs(sources, profile)
    airtable = AirtableClient(settings)
    output_dir = ROOT / "output" / "resumes"

    missing_skills: list[str] = []
    application_records: list[dict[str, object]] = []
    telegram_lines = ["🚀 Career OS job scan complete", f"Found {len(jobs)} aerospace-relevant leads.\n"]

    for index, job in enumerate(jobs[:10], start=1):
        resume_path = create_tailored_resume(profile, job, output_dir)
        cover_letter = generate_cover_letter(settings, profile, job)
        cover_path = Path(str(resume_path).replace("resume_", "cover_letter_").replace(".docx", ".txt"))
        cover_path.write_text(cover_letter, encoding="utf-8")
        missing_skills.extend(job.missing_skills)

        fields = job.airtable_fields(resume_used=str(resume_path.relative_to(ROOT)))
        fields["Cover Letter"] = str(cover_path.relative_to(ROOT))
        application_records.append(fields)
        telegram_lines.append(f"{index}. {job.company} — {job.role}\nScore: {job.match_score}% | {job.category}\nApply: {job.link}\nResume: {resume_path.name}\n")

    airtable.create_records(settings.airtable_applications_table, application_records)
    send_telegram(settings, "\n".join(telegram_lines))
    return missing_skills


def run_skills(settings: Settings, missing_skills: list[str] | None = None) -> None:
    profile = load_profile()
    daily_task = choose_daily_skill(profile, missing_skills or [])
    AirtableClient(settings).create_record(settings.airtable_daily_tasks_table, daily_task)
    send_telegram(
        settings,
        "🛠️ Daily aerospace skill task\n"
        f"Skill: {daily_task['Skill']}\n"
        f"Task: {daily_task['Task']}\n"
        f"Resource: {daily_task['Resource']}\n"
        "Output rule: produce one small proof-of-work artifact before marking complete.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Aman's free aerospace career automation system")
    parser.add_argument("--mode", choices=["all", "jobs", "skills"], default="all")
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.mode == "jobs":
        run_jobs(settings)
    elif args.mode == "skills":
        run_skills(settings)
    else:
        missing = run_jobs(settings)
        run_skills(settings, missing)


if __name__ == "__main__":
    main()
