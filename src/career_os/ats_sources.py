from __future__ import annotations

import logging

from .http import get_json, post_json
from .models import JobLead
from .scoring import keyword_hits, score_job

LOGGER = logging.getLogger(__name__)


def _is_valid_link(link: str) -> bool:
    return link.startswith("http://") or link.startswith("https://")


def _scored_lead(
    *,
    company: str,
    role: str,
    location: str,
    link: str,
    snippet: str,
    source_name: str,
    keywords: list[str],
    blocked_keywords: list[str],
    profile: dict,
) -> JobLead | None:
    text = " ".join([company, role, location, snippet])
    if blocked_keywords and keyword_hits(text, blocked_keywords):
        return None
    if keywords and not keyword_hits(text, keywords):
        return None
    if not _is_valid_link(link):
        return None
    score, category, missing = score_job(text, profile)
    if score < 45:
        return None
    return JobLead(
        company=company or "Unknown company",
        role=role or "Open role",
        category=category,
        location=location or "India / see posting",
        link=link,
        source=source_name,
        snippet=snippet[:500],
        match_score=score,
        missing_skills=missing,
    )


def fetch_greenhouse_leads(source: dict, keywords: list[str], blocked_keywords: list[str], profile: dict) -> list[JobLead]:
    if not source.get("enabled", True):
        return []
    board = str(source.get("board", "")).strip()
    if not board:
        return []
    company = str(source.get("company") or source.get("name") or board).strip()
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    try:
        payload = get_json(url, timeout=25)
    except RuntimeError as exc:
        LOGGER.warning("Greenhouse fetch failed for board %s: %s", board, exc)
        return []
    leads: list[JobLead] = []
    for item in payload.get("jobs", []):
        lead = _scored_lead(
            company=company,
            role=str(item.get("title", "")).strip(),
            location=str(item.get("location", {}).get("name", "")).strip(),
            link=str(item.get("absolute_url", "")).strip(),
            snippet=str(item.get("updated_at", "")).strip(),
            source_name=f"Greenhouse:{board}",
            keywords=keywords,
            blocked_keywords=blocked_keywords,
            profile=profile,
        )
        if lead:
            leads.append(lead)
    return leads


def fetch_lever_leads(source: dict, keywords: list[str], blocked_keywords: list[str], profile: dict) -> list[JobLead]:
    if not source.get("enabled", True):
        return []
    board = str(source.get("board", "")).strip()
    if not board:
        return []
    company = str(source.get("company") or source.get("name") or board).strip()
    url = f"https://api.lever.co/v0/postings/{board}"
    try:
        payload = get_json(url, params={"mode": "json"}, timeout=25)
    except RuntimeError as exc:
        LOGGER.warning("Lever fetch failed for board %s: %s", board, exc)
        return []

    entries = payload if isinstance(payload, list) else []
    leads: list[JobLead] = []
    for item in entries:
        lead = _scored_lead(
            company=company,
            role=str(item.get("text", "")).strip(),
            location=str(item.get("categories", {}).get("location", "")).strip(),
            link=str(item.get("hostedUrl", "")).strip(),
            snippet=str(item.get("descriptionPlain", "")).strip(),
            source_name=f"Lever:{board}",
            keywords=keywords,
            blocked_keywords=blocked_keywords,
            profile=profile,
        )
        if lead:
            leads.append(lead)
    return leads


def fetch_ashby_leads(source: dict, keywords: list[str], blocked_keywords: list[str], profile: dict) -> list[JobLead]:
    if not source.get("enabled", True):
        return []
    board = str(source.get("board", "")).strip()
    if not board:
        return []
    company = str(source.get("company") or source.get("name") or board).strip()
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
    try:
        payload = post_json(url, {"includeCompensation": False}, timeout=25)
    except RuntimeError as exc:
        LOGGER.warning("Ashby fetch failed for board %s: %s", board, exc)
        return []

    entries = payload.get("jobs", [])
    leads: list[JobLead] = []
    for item in entries:
        lead = _scored_lead(
            company=company,
            role=str(item.get("title", "")).strip(),
            location=str(item.get("location", "")).strip(),
            link=str(item.get("jobUrl", "")).strip(),
            snippet=str(item.get("descriptionHtml", "")).strip(),
            source_name=f"Ashby:{board}",
            keywords=keywords,
            blocked_keywords=blocked_keywords,
            profile=profile,
        )
        if lead:
            leads.append(lead)
    return leads
