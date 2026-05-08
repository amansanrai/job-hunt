from __future__ import annotations

import json
import logging
import re
from urllib.parse import quote

from .config import Settings
from .http import get_json, post_json

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
        # Handle both "Notes" and escaped \"Notes\" from JSON response body
        for pattern in [
            r'Unknown field name: \\"([^\\]+)\\"',
            r'Unknown field name: "([^"]+)"',
            r"UNKNOWN_FIELD_NAME.*?Unknown field name.*?(\w[\w ]+\w)",
        ]:
            match = re.search(pattern, error_msg)
            if match:
                return match.group(1).strip()
        return None

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
                        "Airtable write failed for table %r. Error: %s",
                        table, exc,
                    )
                    return False
        return False

    def has_record_for_date(self, table: str, date_value: str, date_field: str = "Date") -> bool:
        if not self.enabled:
            return False
        formula = f"{{{date_field}}}='{date_value}'"
        try:
            response = get_json(
                self._url(table),
                params={"filterByFormula": formula, "maxRecords": "1"},
                headers=self._headers(),
                timeout=30,
            )
        except RuntimeError as exc:
            LOGGER.warning("Airtable read failed for table %r while checking date %r. Error: %s", table, date_value, exc)
            return False
        records = response.get("records", [])
        return isinstance(records, list) and len(records) > 0

    def create_records(self, table: str, records: list[dict[str, object]]) -> int:
        success_count = 0
        for fields in records:
            if self.create_record(table, fields):
                success_count += 1
        return success_count
