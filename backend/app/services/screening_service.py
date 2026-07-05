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
from app.ai.parser import parse_resume, extract_text
from app.ai.embeddings import calculate_similarity
from app.ai.context_builder import compute_parser_confidence, build_candidate_context

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
        
        # Reset force_offline_mode at the start of each new campaign screening run
        self.orchestrator.force_offline_mode = False
        
        # 1. Parse Job Description Requirements
        jd_requirements = extract_jd_requirements(jd_text, role_title)
        
        candidates_raw = []
        
        # 2. Extract and Parse Resumes
        for resume in resumes:
            filename = resume["filename"]
            raw_text = resume["content"]
            
            # Resolve file content if raw_text points to a valid temp file path
            if os.path.exists(raw_text) and os.path.isfile(raw_text):
                try:
                    actual_text = extract_text(raw_text)
                except Exception as e:
                    print(f"    ⚠️  Failed to extract text from path {raw_text}: {e}")
                    actual_text = raw_text
            else:
                actual_text = raw_text
            
            parsed_profile = parse_resume(actual_text, filename)
            
            # Compute parser confidence immediately after parsing
            exp_years_check = get_experience_years(parsed_profile.get("experience", []))
            parser_confidence = compute_parser_confidence(parsed_profile, exp_years_check)
            
            candidates_raw.append({
                "filename": filename,
                "profile": parsed_profile,
                "parser_confidence": parser_confidence,
            })

        # 3. Match and Rank Candidates
        scored_candidates = []
        for item in candidates_raw:
            filename           = item["filename"]
            profile            = item["profile"]
            parser_confidence  = item["parser_confidence"]
            
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

            # FIX 1: semantic_score is on 0-100 scale, normalize to 0-1 before weighted sum
            # W_SEMANTIC=0.50, W_SKILLS=0.25, W_EXPERIENCE=0.15, W_EDUCATION=0.10 → final is 0-100
            overall_score = (
                0.50 * (semantic_score / 100.0 * 100)   # stays 0-100
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
            
            # FIX 2: Case-insensitive skill intersection so "Python" == "python"
            candidate_skills_lower = {s.lower(): s for s in profile.get("skills", [])}
            jd_skills_lower       = {s.lower(): s for s in jd_requirements.get("required_skills", [])}
            matched_skills = sorted([candidate_skills_lower[k] for k in candidate_skills_lower if k in jd_skills_lower])
            missing_skills  = sorted([jd_skills_lower[k]       for k in jd_skills_lower       if k not in candidate_skills_lower])
            
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

            scores_dict = {
                "semantic":   round(semantic_score, 1),
                "skills":     round(skills_score, 1),
                "experience": round(experience_score, 1),
                "education":  round(education_score, 1),
            }

            # Build structured context (the LLM will receive this, not raw text)
            candidate_context = build_candidate_context(
                profile=profile,
                jd_requirements=jd_requirements,
                scores=scores_dict,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                experience_years=exp_years,
                education_degree=edu_label,
                overall_score=overall_score,
            )

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
                "scores": scores_dict,
                "score_breakdown": candidate_context["score_breakdown"],
                "parser_confidence": parser_confidence,
                "experience_years": exp_years,
                "education_degree": edu_label,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "why_reasoning": why_reasons,
                "risk_factors": risk_factors,
                "raw_profile": profile,
                "candidate_context": candidate_context,
                "model_used": "Offline Rule Engine",
                "latency": 0.0,
                "routing_trace": [],
            })

        # Sort candidates descending
        scored_candidates.sort(key=lambda x: x["overall_score"], reverse=True)

        # 4. Generate Recruiter Briefs & Targeted Questions
        for idx, cand in enumerate(scored_candidates):
            # FIX 3: Pass structured scoring context — LLM must NOT invent any data.
            # It only receives computed facts and must explain them.
            prompt = RECRUITER_INSIGHTS_PROMPT.format(
                name=cand["name"],
                role_title=jd_requirements["role_title"],
                overall_score=round(cand["overall_score"], 1),
                semantic_score=round(cand["scores"]["semantic"], 1),
                skills_score=round(cand["scores"]["skills"], 1),
                experience_score=round(cand["scores"]["experience"], 1),
                education_score=round(cand["scores"]["education"], 1),
                experience_years=cand["experience_years"],
                education_degree=cand["education_degree"],
                matched_skills=", ".join(cand["matched_skills"]) or "None detected",
                missing_skills=", ".join(cand["missing_skills"]) or "None",
                required_years=jd_requirements["required_years"],
                required_education_label=jd_requirements["required_education_label"],
                candidate_all_skills=", ".join(cand["raw_profile"].get("skills", [])) or "None detected"
            )
            
            orchestrator_res = self.orchestrator.call_json("summary", prompt, RECRUITER_SYSTEM_PROMPT)
            insights = orchestrator_res.get("json_data")
            cand["model_used"]    = orchestrator_res.get("model_used", "Offline Rule Engine")
            cand["latency"]       = orchestrator_res.get("latency", 0.0)
            cand["routing_trace"] = orchestrator_res.get("routing_trace", [])
            
            if insights:
                cand["recruiter_brief"] = insights.get("recruiter_brief", "")
                cand["strengths"] = insights.get("strengths", [])
                cand["weaknesses"] = insights.get("weaknesses", [])
                cand["interview_questions"] = insights.get("interview_questions", [])
            else:
                # Offline fallback — data-driven, no hallucination
                skills_match_str = ", ".join(cand['matched_skills'][:5]) if cand['matched_skills'] else "none detected"
                missing_str = ", ".join(cand['missing_skills'][:3]) if cand['missing_skills'] else "none"
                semantic_pct = round(cand['scores']['semantic'], 1)
                skill_pct    = round(cand['scores']['skills'], 1)
                exp_pct      = round(cand['scores']['experience'], 1)

                cand["recruiter_brief"] = (
                    f"{cand['name']} scored {cand['overall_score']}/100 overall and is classified as a {cand['match_status']} "
                    f"for the {jd_requirements['role_title']} role. "
                    f"Semantic profile alignment is {semantic_pct}%, skill match is {skill_pct}%, "
                    f"and experience match is {exp_pct}% ({cand['experience_years']} yrs vs {jd_requirements['required_years']} yrs required). "
                    f"Matched skills: {skills_match_str}."
                )
                cand["strengths"] = [
                    s for s in [
                        f"Matched {len(cand['matched_skills'])} of {len(jd_requirements.get('required_skills', []))} required skills: {skills_match_str}." if cand['matched_skills'] else None,
                        f"Possesses {cand['experience_years']} years of professional experience." if cand['experience_years'] > 0 else None,
                        f"Education: {cand['education_degree']}." if cand['education_degree'] and cand['education_degree'] != 'Not Specified' else None,
                        f"Strong semantic profile alignment ({semantic_pct}%) with the job description." if semantic_pct >= 60 else None,
                    ] if s is not None
                ] or ["Profile data available for evaluation."]

                cand["weaknesses"] = [
                    s for s in [
                        f"Missing required skills: {missing_str}." if cand['missing_skills'] else None,
                        f"Experience gap: {cand['experience_years']} yrs found vs {jd_requirements['required_years']} yrs required." if cand['experience_years'] < jd_requirements.get('required_years', 0) else None,
                        f"Education mismatch: found {cand['education_degree']}, role requires {jd_requirements['required_education_label']}." if cand['scores']['education'] < 70 else None,
                    ] if s is not None
                ] or ["No critical gaps identified from available data."]

                first_missing = cand['missing_skills'][0] if cand['missing_skills'] else "core technologies"
                first_matched = cand['matched_skills'][0] if cand['matched_skills'] else "your primary tools"
                cand["interview_questions"] = [
                    f"You appear to be missing {first_missing} from the job requirements — can you describe any adjacent experience or how quickly you could get up to speed?",
                    f"This role requires {jd_requirements['required_years']} years of experience. Walk me through your most relevant {jd_requirements['role_title']} project.",
                    f"Tell me about the most complex thing you've built using {first_matched}.",
                ]

        processing_time = round(time.time() - start_time, 2)

        return {
            "run_id": run_id,
            "role_title": jd_requirements["role_title"],
            "job_description": jd_text,
            "processing_time": processing_time,
            "candidates": scored_candidates
        }

