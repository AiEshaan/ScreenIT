from pathlib import Path
from app.ai.parser import parse_resume, extract_text

def test_resume_parser():
    resume_path = Path("sample_data/resumes/priya_sharma_strong.txt")
    text = extract_text(str(resume_path))
    profile = parse_resume(text, filename="priya_sharma_strong.txt", use_llm=False)
    
    assert isinstance(profile, dict)
    assert "skills" in profile
    assert len(profile["skills"]) > 0
    assert profile["email"] == "priya.sharma@email.com"
