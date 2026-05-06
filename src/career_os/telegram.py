from __future__ import annotations

import logging

from .config import Settings
from .http import post_json

LOGGER = logging.getLogger(__name__)


def send_telegram(settings: Settings, message: str) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id or settings.dry_run:
        LOGGER.info("DRY RUN Telegram message:\n%s", message)
        return
    post_json(
        f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
        {"chat_id": settings.telegram_chat_id, "text": message, "disable_web_page_preview": False},
        timeout=30,
    )
