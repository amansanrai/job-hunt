from __future__ import annotations

import logging

from .config import Settings
from .http import post_json

LOGGER = logging.getLogger(__name__)


def send_telegram(settings: Settings, message: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id or settings.dry_run:
        LOGGER.info("DRY RUN Telegram message:\n%s", message)
        return True
    if not message or not message.strip():
        LOGGER.warning("Telegram message was empty, skipping send.")
        return False
    # Telegram has 4096 char limit
    text = message[:4000]
    try:
        post_json(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            {"chat_id": settings.telegram_chat_id, "text": text, "disable_web_page_preview": False},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
    except RuntimeError as exc:
        LOGGER.error("Telegram send failed. Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID. Error: %s", exc)
        return False
    return True
