from __future__ import annotations

from dataclasses import asdict

from .config import Settings

REQUIRED_FOR_LIVE = [
    ("airtable_token", "AIRTABLE_API_KEY or AIRTABLE_TOKEN"),
    ("airtable_base_id", "AIRTABLE_BASE_ID"),
    ("telegram_bot_token", "TELEGRAM_BOT_TOKEN"),
    ("telegram_chat_id", "TELEGRAM_CHAT_ID"),
]


def check_settings(settings: Settings) -> list[str]:
    messages: list[str] = []
    data = asdict(settings)
    for attr, env_name in REQUIRED_FOR_LIVE:
        if data.get(attr):
            messages.append(f"OK: {env_name} is configured")
        else:
            messages.append(f"MISSING: {env_name}")
    if settings.nvidia_api_key:
        messages.append("OK: NVIDIA_API_KEY is configured for AI cover letters")
    else:
        messages.append("OPTIONAL: NVIDIA_API_KEY is not set; local fallback cover letters will be used")
    if settings.dry_run:
        messages.append("OK: DRY_RUN=true, no Airtable or Telegram writes will be sent")
    return messages


def format_doctor_report(settings: Settings) -> str:
    return "\n".join(["Career OS activation check", *check_settings(settings)])
