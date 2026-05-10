from __future__ import annotations

import logging

from .config import Settings
from .http import get_json
from .models import JobLead
from .scoring import keyword_hits, score_job

LOGGER = logging.getLogger(__name__)

ADZUNA_URL_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def _as_text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _is_valid_link(link: str) -> bool:
    return link.startswith("http://") or link.startswith("https://")


def fetch_adzuna_leads(
    settings: Settings,
    source: dict,
    keywords: list[str],
    blocked_keywords: list[str],
    profile: dict,
) -> list[JobLead]:
    if not source.get("enabled", True):
        return []
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        LOGGER.info("Adzuna source skipped because ADZUNA_APP_ID/ADZUNA_APP_KEY are not configured.")
        return []

    country = _as_text(source.get("country", "in")).lower() or "in"
    pages = max(1, min(int(source.get("pages", 1) or 1), 3))
    results_per_page = max(1, min(int(source.get("results_per_page", 20) or 20), 50))

    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": str(results_per_page),
        "what_or": _as_text(source.get("what_or", "aerospace drone uav cfd cad simulation")),
        "where": _as_text(source.get("where", "India")),
        "sort_by": _as_text(source.get("sort_by", "date")) or "date",
        "content-type": "application/json",
    }

    leads: list[JobLead] = []
    for page in range(1, pages + 1):
        url = ADZUNA_URL_TEMPLATE.format(country=country, page=page)
        try:
            payload = get_json(url, params=params, headers={"User-Agent": "career-os/0.1"}, timeout=25)
        except RuntimeError as exc:
            LOGGER.warning("Adzuna fetch failed for page %s: %s", page, exc)
            continue

        for item in payload.get("results", []):
            title = _as_text(item.get("title"))
            company = _as_text(item.get("company", {}).get("display_name")) or "Unknown company"
            location = _as_text(item.get("location", {}).get("display_name")) or "India / see posting"
            description = _as_text(item.get("description"))
            link = _as_text(item.get("redirect_url") or item.get("adref"))
            text = " ".join(part for part in [title, company, location, description] if part)

            if not _is_valid_link(link):
                continue
            if blocked_keywords and keyword_hits(text, blocked_keywords):
                continue
            if keywords and not keyword_hits(text, keywords):
                continue

            score, category, missing = score_job(text, profile)
            if score < 45:
                continue
            leads.append(
                JobLead(
                    company=company,
                    role=title or "Open role",
                    category=category,
                    location=location,
                    link=link,
                    source="Adzuna API",
                    snippet=description[:500],
                    match_score=score,
                    missing_skills=missing,
                )
            )
    return leads
