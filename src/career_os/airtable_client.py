from __future__ import annotations

import json
import logging
import re
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

    def _extract_unknown_field(self, error_msg: str) -> str | None:
        """Extract field name from Airtable UNKNOWN_FIELD_NAME error."""
        match = re.search(r'Unknown field name: "([^"]+)"', error_msg)
        return match.group(1) if match else None

    def create_record(self, table: str, fields: dict[str, object]) -> bool:
        if not self.enabled:
            LOGGER.info("DRY RUN Airtable %s: %s", table, fields)
            return True

        remaining_fields = dict(fields)
        max_retries = 3

        for attempt in range(max_retries):
            try:
                post_json(self._url(table), {"fields": remaining_fields, "typecast": True}, headers=self._headers(), timeout=30)
                return True
            except RuntimeError as exc:
                error_str = str(exc)
                unknown_field = self._extract_unknown_field(error_str)
                if unknown_field and unknown_field in remaining_fields and attempt < max_retries - 1:
                    LOGGER.warning(
                        "Airtable table %r does not have field %r. Dropping it and retrying. "
                        "Add this field to your Airtable table to stop this warning.",
                        table, unknown_field,
                    )
                    del remaining_fields[unknown_field]
                    continue
                else:
                    LOGGER.error(
                        "Airtable write failed for table %r. Check token base access, data.records:write scope, "
                        "table name, and field names. Error: %s",
                        table,
                        exc,
                    )
                    return False
        return False

    def create_records(self, table: str, records: list[dict[str, object]]) -> int:
        success_count = 0
        for fields in records:
            if self.create_record(table, fields):
                success_count += 1
        return success_count
