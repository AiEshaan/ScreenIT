# backend/app/services/screening_service.py
import os
import sys
import uuid
import time
from typing import List, Dict, Any

# Adjust paths to make sure we can import from original resume_screening and shared
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from app.ai.extractor import extract_jd_requirements, get_education_level, get_experience_years
from app.ai.ranking import score_candidate

from app.ai.llm_orchestrator import AIOrchestrator
from app.ai.parser import parse_resume
from app.ai.embeddings import calculate_similarity


from shared.prompts.screening_prompts import RECRUITER_INSIGHTS_PROMPT, RECRUITER_SYSTEM_PROMPT


class AIEngine:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def process_screening(self, jd_text: str, role_title: str, resumes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs the end-to-end recruiter screening workflow.
        Keeps track of telemetry processing times to display in stats.
        """
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        # 1. Parse Job Description Requirements
        jd_requirements = extract_jd_requirements(jd_text, role_title)
        
        candidates_raw = []
        
        # 2. Extract and Parse Resumes
        for resume in resumes:
            filename = resume["filename"]
            raw_text = resume["content"]
            
            parsed_profile = parse_resume(raw_text, filename)
            candidates_raw.append({
                "filename": filename,
                "profile": parsed_profile
            })

        # 3. Match and Rank Candidates
        scored_candidates = []
        for item in candidates_raw:
            filename = item["filename"]
            profile = item["profile"]
            
            # Local scoring (SentenceTransformer semantic match + skills + exp + edu)
            score_data = score_candidate(profile, jd_requirements)
            
            # Extract experience and education metadata
            exp_years = get_experience_years(profile.get("experience", []))
            edu_level, edu_label = get_education_level(profile.get("education", []))
            
            # Compute semantic score using our modular embedding model
            resume_full_text = " ".join([
                profile.get("summary", ""),
                " ".join(profile.get("skills", [])),
                " ".join([e.get("description", "") for e in profile.get("experience", [])])
            ])
            try:
                semantic_score = calculate_similarity(resume_full_text, jd_text)
            except Exception:
                semantic_score = score_data["breakdown"]["semantic_similarity"]

            # Compute category breakdowns
            skills_score = score_data["breakdown"]["skill_match"]
            experience_score = score_data["breakdown"]["experience_match"]
            education_score = score_data["breakdown"]["education_match"]

            # Compute algorithm weighted score
            # ScreenIt uses the ranking weight values: W_SEMANTIC = 0.50, W_SKILLS = 0.25, W_EXPERIENCE = 0.15, W_EDUCATION = 0.10
            overall_score = (
                0.50 * semantic_score
                + 0.25 * skills_score
                + 0.15 * experience_score
                + 0.10 * education_score
            )
            
            # Determine match status and recruiter confidence
            if overall_score >= 80:
                match_status, confidence = "Strong Match", "High"
            elif overall_score >= 65:
                match_status, confidence = "Good Match", "Medium"
            elif overall_score >= 50:
                match_status, confidence = "Moderate Match", "Medium"
            else:
                match_status, confidence = "Weak Match", "Low"
            
            matched_skills = sorted(list(set(profile.get("skills", [])) & set(jd_requirements.get("required_skills", []))))
            missing_skills = sorted(list(set(jd_requirements.get("required_skills", [])) - set(profile.get("skills", []))))
            
            # Explainability: Why Ranked List
            why_reasons = []
            if exp_years >= jd_requirements.get("required_years", 0):
                why_reasons.append(f"Exceeds role required experience ({exp_years} yrs vs {jd_requirements.get('required_years', 0)} yrs required)")
            else:
                why_reasons.append(f"Below ideal required experience years ({exp_years} yrs vs {jd_requirements.get('required_years', 0)} yrs required)")
                
            if semantic_score >= 70:
                why_reasons.append(f"Strong semantic profile alignment ({round(semantic_score)}%) with Job Description")
                
            if len(matched_skills) > 0:
                why_reasons.append(f"Matches key technical skills: {', '.join(matched_skills[:3])}")

            # Risk Factors list
            risk_factors = []
            if len(missing_skills) > 0:
                risk_factors.append(f"Missing core skills: {', '.join(missing_skills[:3])}")
            if exp_years < jd_requirements.get("required_years", 0):
                risk_factors.append("Below target experience duration requirements")

            scored_candidates.append({
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "name": profile.get("name") or filename.split(".")[0].replace("_", " ").title(),
                "email": profile.get("email"),
                "phone": profile.get("phone"),
                "linkedin": profile.get("linkedin"),
                "github": profile.get("github"),
                "overall_score": round(overall_score, 1),
                "confidence": confidence,
                "match_status": match_status,
                "scores": {
                  "semantic": round(semantic_score, 1),
                  "skills": round(skills_score, 1),
                  "experience": round(experience_score, 1),
                  "education": round(education_score, 1)
                },
                "experience_years": exp_years,
                "education_degree": edu_label,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "why_reasoning": why_reasons,
                "risk_factors": risk_factors,
                "raw_profile": profile,
                "model_used": "Offline Rule Engine",
                "latency": 0.0
            })

        # Sort candidates descending
        scored_candidates.sort(key=lambda x: x["overall_score"], reverse=True)

        # 4. Generate Recruiter Briefs & Targeted Questions
        for idx, cand in enumerate(scored_candidates):
            prompt = RECRUITER_INSIGHTS_PROMPT.format(
                name=cand["name"],
                role_title=jd_requirements["role_title"],
                experience_years=cand["experience_years"],
                education_degree=cand["education_degree"],
                matched_skills=", ".join(cand["matched_skills"]),
                missing_skills=", ".join(cand["missing_skills"]),
                required_years=jd_requirements["required_years"],
                required_education_label=jd_requirements["required_education_label"]
            )
            
            orchestrator_res = self.orchestrator.call_json("summary", prompt, RECRUITER_SYSTEM_PROMPT)
            insights = orchestrator_res.get("json_data")
            cand["model_used"] = orchestrator_res.get("model_used", "Offline Rule Engine")
            cand["latency"] = orchestrator_res.get("latency", 0.0)
            
            if insights:
                cand["recruiter_brief"] = insights.get("recruiter_brief", "")
                cand["strengths"] = insights.get("strengths", [])
                cand["weaknesses"] = insights.get("weaknesses", [])
                cand["interview_questions"] = insights.get("interview_questions", [])
            else:
                # Local fallbacks
                skills_match_str = ", ".join(cand['matched_skills'][:4]) if cand['matched_skills'] else "none"
                cand["recruiter_brief"] = (
                    f"{cand['name']} scored {cand['overall_score']}/100 and is classified as a {cand['match_status']}. "
                    f"They possess {cand['experience_years']} years of experience and have matched skills including: {skills_match_str}."
                )
                cand["strengths"] = [
                    f"Possesses {cand['experience_years']} years of professional experience.",
                    f"Demonstrated competence in {len(cand['matched_skills'])} matched skills."
                ]
                cand["weaknesses"] = [
                    f"Missing required skills: {', '.join(cand['missing_skills'][:3])}" if cand['missing_skills'] else "No critical skill gaps identified."
                ]
                cand["interview_questions"] = [
                    f"Can you explain your experience and how you would work around not having hands-on experience in {cand['missing_skills'][0]}?" if len(cand['missing_skills']) > 0 else "What is your experience working with AI tools?",
                    "How do you stay up-to-date with new tools and frameworks in the industry?"
                ]

        processing_time = round(time.time() - start_time, 2)

        return {
            "run_id": run_id,
            "role_title": jd_requirements["role_title"],
            "job_description": jd_text,
            "processing_time": processing_time,
            "candidates": scored_candidates
        }

