from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from .adzuna import fetch_adzuna_leads
from .ats_sources import fetch_ashby_leads, fetch_greenhouse_leads, fetch_lever_leads
from .config import Settings
from .models import JobLead
from .scoring import keyword_hits, score_job

DIRECT_APPLY_TERMS = [
    "apply",
    "job-detail",
    "job_detail",
    "jobdetails",
    "jobs/",
    "careers/jobs",
    "current-openings",
    "opening",
    "greenhouse.io",
    "lever.co",
    "workdayjobs",
    "myworkdayjobs",
    "smartrecruiters",
    "bamboohr",
    "ashbyhq",
    "recruitee",
]

GENERIC_PAGE_TERMS = ["/careers", "/career", "/jobs", "/join-us", "/work-with-us"]


def _path_without_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.rstrip("/").lower()


def is_direct_apply_link(label: str, href: str, keywords: list[str]) -> bool:
    """Return true when a link looks like an actionable job/apply URL."""
    joined = f"{label} {href}".lower()
    if not (keyword_hits(joined, keywords) or any(term in joined for term in DIRECT_APPLY_TERMS)):
        return False
    parsed = urlparse(href)
    if not parsed.scheme.startswith("http"):
        return False
    path = _path_without_trailing_slash(href)
    if path in {"", "/"}:
        return False
    if any(path == term for term in GENERIC_PAGE_TERMS):
        return False
    return True


def seed_job_leads(seed_jobs: dict, profile: dict) -> list[JobLead]:
    leads: list[JobLead] = []
    for item in seed_jobs.get("jobs", []):
        text = " ".join(str(item.get(key, "")) for key in ["company", "role", "category", "location", "link", "notes"])
        score, inferred_category, missing = score_job(text, profile)
        leads.append(
            JobLead(
                company=item.get("company", "Unknown company"),
                role=item.get("role", "Review seeded role"),
                category=item.get("category") or inferred_category,
                location=item.get("location", "India / see posting"),
                link=item.get("link", ""),
                source="seed_jobs.json",
                snippet=item.get("notes", "Manually seeded direct apply link"),
                match_score=max(score, int(item.get("match_score", 0) or 0)),
                missing_skills=missing,
            )
        )
    return [lead for lead in leads if lead.link]


def _lead_hash(lead: JobLead) -> str:
    def _norm(value: str | None) -> str:
        return (value or "").strip().lower()

    parts = [_norm(lead.company), _norm(lead.role), _norm(lead.link)]
    digest_input = "|".join(f"{len(part)}:{part}" for part in parts)
    return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()


def find_jobs(
    sources: dict,
    profile: dict,
    settings: Settings | None = None,
    seed_jobs: dict | None = None,
    limit: int = 15,
) -> list[JobLead]:
    keywords = sources.get("keywords", [])
    blocked_keywords = sources.get("blocked_keywords", [])
    apis = sources.get("apis", {})

    all_leads: list[JobLead] = []
    if seed_jobs:
        all_leads.extend(seed_job_leads(seed_jobs, profile))

    if settings:
        all_leads.extend(fetch_adzuna_leads(settings, apis.get("adzuna", {}), keywords, blocked_keywords, profile))
    for source in apis.get("greenhouse", []):
        all_leads.extend(fetch_greenhouse_leads(source, keywords, blocked_keywords, profile))
    for source in apis.get("lever", []):
        all_leads.extend(fetch_lever_leads(source, keywords, blocked_keywords, profile))
    for source in apis.get("ashby", []):
        all_leads.extend(fetch_ashby_leads(source, keywords, blocked_keywords, profile))

    deduped: dict[str, JobLead] = {}
    for lead in all_leads:
        key = _lead_hash(lead)
        current = deduped.get(key)
        if current is None or lead.match_score > current.match_score:
            deduped[key] = lead
    return sorted(deduped.values(), key=lambda item: item.match_score, reverse=True)[:limit]
