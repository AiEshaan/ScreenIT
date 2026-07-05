# shared/prompts/screening_prompts.py

RECRUITER_INSIGHTS_PROMPT = """\
Analyze the candidate '{name}' for the role '{role_title}'.

Candidate Summary:
- Experience: {experience_years} years
- Highest Education: {education_degree}
- Matched Skills: {matched_skills}
- Missing Skills: {missing_skills}

Role Requirements:
- Required Experience: {required_years} years
- Required Education: {required_education_label}

Return ONLY valid JSON with exactly these keys:
{{
  "recruiter_brief": "A 3-4 sentence professional summary of why they match or don't match, written for a recruiter.",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Gap 1", "Gap 2"],
  "interview_questions": [
    "Question targeting missing skill or gap 1",
    "Question targeting missing skill or gap 2",
    "A general technical question based on their profile"
  ]
}}
"""

RECRUITER_SYSTEM_PROMPT = "You are a professional recruiting coordinator. Provide concise, clear, and objective candidate assessments."
