from career_os.job_finder import is_direct_apply_link, seed_job_leads

KEYWORDS = ["uav", "cfd", "simulation"]


def test_rejects_plain_company_homepage():
    assert not is_direct_apply_link("Careers", "https://example.com/", KEYWORDS)


def test_accepts_direct_apply_link_with_relevant_role():
    assert is_direct_apply_link(
        "UAV Design Intern Apply now",
        "https://example.com/careers/jobs/uav-design-intern/apply",
        KEYWORDS,
    )


def test_seed_jobs_create_actionable_leads():
    profile = {
        "target_roles": ["UAV Engineer"],
        "preferred_categories": ["UAV"],
        "skills": ["SolidWorks basics"],
        "weak_areas": ["PX4"],
    }
    leads = seed_job_leads(
        {
            "jobs": [
                {
                    "company": "Example Aerospace",
                    "role": "UAV Intern",
                    "category": "UAV",
                    "location": "Bangalore",
                    "link": "https://example.com/jobs/uav-intern/apply",
                    "notes": "PX4 exposure preferred",
                }
            ]
        },
        profile,
    )
    assert leads[0].company == "Example Aerospace"
    assert leads[0].link.endswith("/apply")
    assert "PX4" in leads[0].missing_skills
