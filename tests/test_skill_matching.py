from app.ai.similarity import compute_skill_match

def test_skill_matching_case_insensitive():
    jd_skills = ["Python", "FastAPI", "Docker"]
    resume_skills = ["python", "fastapi", "docker"]
    
    result = compute_skill_match(jd_skills, resume_skills)
    assert result["score"] == 100.0
    assert len(result["matched"]) == 3
    assert len(result["missing"]) == 0
