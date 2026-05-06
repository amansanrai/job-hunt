from __future__ import annotations

from collections import Counter
from datetime import date

FREE_RESOURCES = {
    "OpenFOAM": "https://www.openfoam.com/documentation/tutorial-guide",
    "ROS2": "https://docs.ros.org/en/rolling/Tutorials.html",
    "PX4": "https://docs.px4.io/main/en/",
    "mesh independence": "https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html",
    "MATLAB Simulink controls": "https://www.mathworks.com/help/simulink/getting-started-with-simulink.html",
    "sheet metal design": "https://help.solidworks.com/",
}

TASKS = {
    "OpenFOAM": "Run one built-in tutorial case and save one velocity or pressure contour.",
    "ROS2": "Complete one beginner publisher/subscriber tutorial and note the command sequence.",
    "PX4": "Read PX4 architecture docs and summarize the role of flight stack, sensors, and simulation.",
    "mesh independence": "Create a coarse/medium/fine result table for one CFD case and compute percent difference.",
    "MATLAB Simulink controls": "Build a second-order transfer-function step response and record overshoot/settling time.",
    "sheet metal design": "Model one bracket/enclosure, generate a flat pattern, and record thickness/K-factor.",
}


def choose_daily_skill(profile: dict, missing_skills_from_jobs: list[str]) -> dict[str, object]:
    weak_areas = profile.get("weak_areas", [])
    counts = Counter(missing_skills_from_jobs)
    selected = counts.most_common(1)[0][0] if counts else (weak_areas[0] if weak_areas else "mesh independence")
    return {
        "Date": date.today().isoformat(),
        "Skill": selected,
        "Category": "Skill Gap",
        "Task": TASKS.get(selected, f"Spend 30 minutes learning {selected} and create one proof-of-work note."),
        "Difficulty": "Small / 30 min",
        "Completed": False,
        "Resource": FREE_RESOURCES.get(selected, "https://www.youtube.com/results?search_query=free+engineering+tutorial"),
        "Notes": "Generated from repeated job-skill gaps; keep the output small and verifiable.",
    }
