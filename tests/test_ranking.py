from app.ai.ranking import score_candidate

def test_score_is_valid():
    candidate = {
        "name": "Jane Doe",
        "skills": ["Python", "FastAPI"],
        "experience": [{"title": "Engineer", "start": "2020", "end": "2023"}],
        "education": [{"degree": "Bachelor of Technology", "school": "IIT"}],
        "raw_text": "Jane Doe is an engineer skilled in Python and FastAPI. She has a B.Tech."
    }
    
    jd = {
        "text": "We need a python engineer with experience in FastAPI and python.",
        "required_skills": ["Python", "FastAPI"],
        "required_years": 2.0,
        "required_education_level": 2,
        "required_education_label": "Bachelor's"
    }
    
    result = score_candidate(candidate, jd)
    assert result["overall_score"] > 50.0
    assert result["overall_score"] <= 100.0
    assert result["candidate"] == "Jane Doe"
