from career_os.scoring import infer_category, score_job


def test_infers_uav_category():
    assert infer_category("UAV drone flight testing with PX4") == "UAV"


def test_scores_fresher_cfd_role():
    profile = {
        "target_roles": ["CFD Engineer", "UAV Engineer"],
        "preferred_categories": ["CFD", "UAV"],
        "skills": ["ANSYS Fluent basics", "MATLAB basics"],
        "weak_areas": ["OpenFOAM", "mesh independence"],
    }
    score, category, missing = score_job(
        "Graduate trainee CFD engineer using ANSYS Fluent, OpenFOAM and mesh independence for aerospace aerodynamics",
        profile,
    )
    assert category == "CFD"
    assert score >= 60
    assert "OpenFOAM" in missing
