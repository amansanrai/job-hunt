from __future__ import annotations

import re
from collections.abc import Iterable

CATEGORY_KEYWORDS = {
    "Rocketry": ["rocket", "propulsion", "launch vehicle", "gnc", "trajectory", "space"],
    "UAV": ["uav", "drone", "uas", "px4", "ros2", "flight test", "autonomy"],
    "CFD": ["cfd", "fluent", "openfoam", "star-ccm", "aerodynamics", "mesh", "turbulence"],
    "Simulation": ["simulation", "matlab", "simulink", "model based", "cae", "numerical"],
    "CAD": ["cad", "solidworks", "catia", "nx", "creo", "drafting", "sheet metal"],
    "Aerospace Manufacturing": ["manufacturing", "composites", "assembly", "testing", "quality"],
    "Aircraft Documentation": ["aircraft documentation", "technical publication", "maintenance", "manual"],
}

FRESHER_KEYWORDS = ["fresher", "graduate", "trainee", "intern", "entry", "0-1", "0 to 1", "apprentice"]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def keyword_hits(text: str, keywords: Iterable[str]) -> list[str]:
    haystack = normalize(text)
    return [keyword for keyword in keywords if keyword.lower() in haystack]


def infer_category(text: str) -> str:
    scores = {category: len(keyword_hits(text, words)) for category, words in CATEGORY_KEYWORDS.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "Simulation"


def score_job(text: str, profile: dict) -> tuple[int, str, list[str]]:
    combined = normalize(text)
    profile_terms = profile.get("target_roles", []) + profile.get("preferred_categories", []) + profile.get("skills", [])
    hits = keyword_hits(combined, profile_terms)
    category = infer_category(combined)
    freshers = keyword_hits(combined, FRESHER_KEYWORDS)
    penalty = 25 if any(term in combined for term in ["5+ years", "8 years", "senior", "principal"]) else 0
    score = min(95, 30 + len(hits) * 7 + len(freshers) * 8 + (15 if category in profile.get("preferred_categories", []) else 0) - penalty)
    missing = [skill for skill in profile.get("weak_areas", []) if skill.lower() in combined]
    return max(0, score), category, missing
