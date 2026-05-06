from __future__ import annotations

import logging
from urllib.parse import quote

from .config import Settings
from .http import post_json

LOGGER = logging.getLogger(__name__)


class AirtableClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = bool(settings.airtable_token and settings.airtable_base_id and not settings.dry_run)

    def _url(self, table: str) -> str:
        assert self.settings.airtable_base_id is not None
        return f"https://api.airtable.com/v0/{self.settings.airtable_base_id}/{quote(table)}"

    def _headers(self) -> dict[str, str]:
        assert self.settings.airtable_token is not None
        return {"Authorization": f"Bearer {self.settings.airtable_token}", "Content-Type": "application/json"}

    def create_record(self, table: str, fields: dict[str, object]) -> bool:
        if not self.enabled:
            LOGGER.info("DRY RUN Airtable %s: %s", table, fields)
            return True
        try:
            post_json(self._url(table), {"fields": fields, "typecast": True}, headers=self._headers(), timeout=30)
        except RuntimeError as exc:
            LOGGER.error(
                "Airtable write failed for table %r. Check token base access, data.records:write scope, "
                "table name, and field names. Error: %s",
                table,
                exc,
            )
            return False
        return True

    def create_records(self, table: str, records: list[dict[str, object]]) -> int:
        success_count = 0
        for fields in records:
            if self.create_record(table, fields):
                success_count += 1
        return success_count
