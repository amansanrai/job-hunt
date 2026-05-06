from __future__ import annotations

import logging

from .config import Settings
from .http import post_json
from .models import JobLead

LOGGER = logging.getLogger(__name__)


def _fallback_cover_letter(profile: dict, job: JobLead) -> str:
    return (
        f"Dear Hiring Team,\n\n"
        f"I am {profile['name']}, a BTech fresher interested in {job.category} roles. "
        f"Your opening for {job.role} at {job.company} matches my focus on UAV, CFD, CAD, simulation, "
        f"and practical aerospace engineering work. I am building truthful project evidence around airfoil CFD, "
        f"mesh independence, UAV CAD concepts, and engineering documentation.\n\n"
        f"I would value the opportunity to contribute as an entry-level learner while strengthening production-quality "
        f"engineering outputs for your team.\n\nRegards,\n{profile['name']}"
    )


def generate_cover_letter(settings: Settings, profile: dict, job: JobLead) -> str:
    if not settings.nvidia_api_key:
        return _fallback_cover_letter(profile, job)

    prompt = (
        "Write a concise, truthful, non-generic cover letter. Do not invent experience. "
        "Keep it under 180 words.\n"
        f"Candidate profile: {profile}\n"
        f"Job: company={job.company}, role={job.role}, category={job.category}, notes={job.snippet}"
    )
    try:
        payload = post_json(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            {
                "model": settings.nvidia_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 350,
            },
            headers={"Authorization": f"Bearer {settings.nvidia_api_key}", "Content-Type": "application/json"},
            timeout=45,
        )
        return payload["choices"][0]["message"]["content"].strip()
    except (RuntimeError, KeyError, IndexError) as exc:
        LOGGER.warning("NVIDIA generation failed; using fallback: %s", exc)
        return _fallback_cover_letter(profile, job)


def tailor_resume_summary(profile: dict, job: JobLead) -> str:
    skills = ", ".join(profile.get("skills", [])[:6])
    return (
        f"{profile['name']} is a BTech fresher targeting {job.category} roles, with current practice in {skills}. "
        f"For {job.company}'s {job.role}, emphasize truthful project evidence: airfoil CFD outputs, UAV CAD concepts, "
        f"MATLAB/Simulink basics, and engineering documentation."
    )
