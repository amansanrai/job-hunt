from __future__ import annotations

import logging
import re
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse

from .http import get_text
from .models import JobLead
from .scoring import keyword_hits, score_job

LOGGER = logging.getLogger(__name__)

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


class LinkTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []
        self.text_parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "a":
            attrs_dict = dict(attrs)
            self._href = attrs_dict.get("href")
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "a" and self._href:
            label = " ".join(" ".join(self._text).split())
            self.links.append((unescape(label), self._href))
            self._href = None
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        clean = " ".join(data.split())
        if clean:
            self.text_parts.append(clean)
            if self._href:
                self._text.append(clean)

    @property
    def page_text(self) -> str:
        return unescape(" ".join(self.text_parts))


def _path_without_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.rstrip("/").lower()


def is_direct_apply_link(label: str, href: str, keywords: list[str]) -> bool:
    """Return true only for links likely to be actionable job/apply URLs.

    This intentionally rejects plain company homepages or generic careers landing pages by default,
    because the workflow should notify Aman with links he can click and use immediately.
    """
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


def _candidate_links(base_url: str, links: list[tuple[str, str]], keywords: list[str]) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for label, href in links:
        absolute_href = urljoin(base_url, href)
        if is_direct_apply_link(label or absolute_href, absolute_href, keywords):
            candidates.append((label or absolute_href, absolute_href))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for label, href in candidates:
        normalized_href = re.sub(r"#.*$", "", href)
        if normalized_href not in seen:
            seen.add(normalized_href)
            unique.append((label, normalized_href))
    return unique[:20]


def fetch_page_leads(source: dict, keywords: list[str], blocked_keywords: list[str], profile: dict) -> list[JobLead]:
    url = source["url"]
    headers = {"User-Agent": "career-os/0.1 (+manual job research; respectful low-frequency checks)"}
    try:
        html = get_text(url, headers=headers, timeout=20)
    except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
        LOGGER.warning("Could not fetch %s: %s", url, exc)
        return []

    parser = LinkTextParser()
    parser.feed(html)
    page_text = parser.page_text
    blocked = keyword_hits(page_text, blocked_keywords)
    if blocked:
        LOGGER.info("Skipping %s because blocked keywords were found: %s", url, blocked)
        return []

    leads: list[JobLead] = []
    if source.get("allow_discovery_page", False) and keyword_hits(page_text, keywords):
        score, category, missing = score_job(page_text, profile)
        leads.append(
            JobLead(
                company=source["name"].replace(" Careers", ""),
                role="Discovery page match - find exact apply link before applying",
                category=category,
                location="India / see posting",
                link=url,
                source=source["name"],
                snippet=page_text[:500],
                match_score=max(0, score - 20),
                missing_skills=missing,
            )
        )

    for label, href in _candidate_links(url, parser.links, keywords):
        text = f"{label} {href}"
        if keyword_hits(text, blocked_keywords):
            continue
        score, category, missing = score_job(text, profile)
        if score >= 45:
            leads.append(
                JobLead(
                    company=source["name"].replace(" Careers", ""),
                    role=label[:120] or "Open role",
                    category=category,
                    location="India / see posting",
                    link=href,
                    source=source["name"],
                    snippet=f"Direct apply candidate: {text[:450]}",
                    match_score=score,
                    missing_skills=missing,
                )
            )
    return leads


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


def find_jobs(sources: dict, profile: dict, seed_jobs: dict | None = None, limit: int = 15) -> list[JobLead]:
    keywords = sources.get("keywords", [])
    blocked_keywords = sources.get("blocked_keywords", [])
    all_leads: list[JobLead] = []
    if seed_jobs:
        all_leads.extend(seed_job_leads(seed_jobs, profile))
    for source in sources.get("pages", []):
        all_leads.extend(fetch_page_leads(source, keywords, blocked_keywords, profile))
    deduped: dict[str, JobLead] = {}
    for lead in all_leads:
        current = deduped.get(lead.link)
        if current is None or lead.match_score > current.match_score:
            deduped[lead.link] = lead
    return sorted(deduped.values(), key=lambda item: item.match_score, reverse=True)[:limit]
