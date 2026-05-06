from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def clean_env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value else None


@dataclass(frozen=True)
class Settings:
    airtable_token: str | None
    airtable_base_id: str | None
    airtable_applications_table: str
    airtable_skills_table: str
    airtable_daily_tasks_table: str
    airtable_resume_versions_table: str
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    nvidia_api_key: str | None
    nvidia_model: str
    dropbox_token: str | None
    dry_run: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            airtable_token=clean_env("AIRTABLE_API_KEY") or clean_env("AIRTABLE_TOKEN"),
            airtable_base_id=clean_env("AIRTABLE_BASE_ID"),
            airtable_applications_table=os.getenv("AIRTABLE_APPLICATIONS_TABLE", "Applications"),
            airtable_skills_table=os.getenv("AIRTABLE_SKILLS_TABLE", "Skills"),
            airtable_daily_tasks_table=os.getenv("AIRTABLE_DAILY_TASKS_TABLE", "Daily Tasks"),
            airtable_resume_versions_table=os.getenv("AIRTABLE_RESUME_VERSIONS_TABLE", "Resume Versions"),
            telegram_bot_token=clean_env("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=clean_env("TELEGRAM_CHAT_ID"),
            nvidia_api_key=clean_env("NVIDIA_API_KEY"),
            nvidia_model=os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct"),
            dropbox_token=clean_env("DROPBOX_TOKEN"),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        )


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_profile() -> dict[str, Any]:
    return load_json(ROOT / "data" / "master_profile.json")


def load_sources() -> dict[str, Any]:
    return load_json(ROOT / "data" / "sources.json")


def load_seed_jobs() -> dict[str, Any]:
    path = ROOT / "data" / "seed_jobs.json"
    if not path.exists():
        return {"jobs": []}
    return load_json(path)
