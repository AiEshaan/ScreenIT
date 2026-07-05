"""
resume_screening/ranking.py
-----------------------------
Candidate scoring, ranking, and LLM-powered recruiter note generation.

Scoring formula (weights reflect real ATS system priorities):
  ┌────────────────────────┬───────┬────────────────────────────────────────┐
  │ Dimension              │ Weight│ Rationale                              │
  ├────────────────────────┼───────┼────────────────────────────────────────┤
  │ Semantic Similarity    │  50%  │ Overall alignment of candidate profile │
  │ Skill Match            │  25%  │ Explicit JD skill requirements         │
  │ Experience Match       │  15%  │ Years of experience vs. requirement    │
  │ Education Match        │  10%  │ Degree level vs. requirement           │
  └────────────────────────┴───────┴────────────────────────────────────────┘

Why NOT logistic regression / LinearSVC?
  These classifiers require labeled training data (résumé + accept/reject label).
  Without ground-truth labels, they'd fit noise and produce meaningless scores.
  A weighted, explainable formula is more honest, more auditable, and is the
  standard approach in real commercial ATS platforms (Workday, Lever, etc.).
"""

from __future__ import annotations

import os
from typing import Optional

from backend.app.ai.extractor import (
    get_education_level,
    get_experience_years,
)
from backend.app.ai.similarity import (
    compute_education_score,
    compute_experience_score,
    compute_semantic_similarity,
    compute_skill_match,
)

# ── Scoring weights ───────────────────────────────────────────────────────────
W_SEMANTIC    = 0.50
W_SKILLS      = 0.25
W_EXPERIENCE  = 0.15
W_EDUCATION   = 0.10


# ── Per-candidate scoring ─────────────────────────────────────────────────────

def score_candidate(candidate: dict, jd_requirements: dict) -> dict:
    """
    Compute the full scoring breakdown for a single candidate.

    Args:
        candidate:       Parsed resume dict (from parser.parse_resume)
        jd_requirements: Parsed JD dict (from extractor.extract_jd_requirements)

    Returns:
        Scoring dict with overall_score, breakdown, matched/missing skills,
        experience & education comparison, and recommendation.
    """
    resume_text = candidate.get("raw_text", "")
    jd_text = jd_requirements.get("text", "")

    # 1. Semantic similarity  (pretrained ML model)
    semantic_score = compute_semantic_similarity(jd_text, resume_text)

    # 2. Skill match  (deterministic set intersection)
    skill_result = compute_skill_match(
        jd_requirements.get("required_skills", []),
        candidate.get("skills", []),
    )

    # 3. Experience match  (parsed date-range calculation)
    experience_years = get_experience_years(candidate.get("experience", []))
    required_years   = jd_requirements.get("required_years", 1.0)
    experience_score = compute_experience_score(experience_years, required_years)

    # 4. Education match  (normalised degree taxonomy)
    edu_level, edu_label = get_education_level(candidate.get("education", []))
    required_edu_level   = jd_requirements.get("required_education_level", 2)
    education_score      = compute_education_score(edu_level, required_edu_level)

    # 5. Weighted final score
    final_score = round(
        W_SEMANTIC   * semantic_score
        + W_SKILLS   * skill_result["score"]
        + W_EXPERIENCE * experience_score
        + W_EDUCATION  * education_score,
        2,
    )

    return {
        "candidate":               candidate.get("name", "Unknown"),
        "file":                    candidate.get("filename", ""),
        "email":                   candidate.get("email", ""),
        "overall_score":           final_score,
        "recommendation":          _get_recommendation(final_score),
        "breakdown": {
            "semantic_similarity": semantic_score,
            "skill_match":         skill_result["score"],
            "experience_match":    experience_score,
            "education_match":     education_score,
        },
        "matched_skills":           skill_result["matched"],
        "missing_skills":           skill_result["missing"],
        "experience_years_found":   experience_years,
        "experience_years_required": required_years,
        "education_found":          edu_label,
        "education_required":       jd_requirements.get("required_education_label", "Bachelor's"),
        "recruiter_notes":          "",  # populated later by generate_recruiter_summary
        "rank":                     0,   # set after sorting
    }


def rank_candidates(
    candidates: list[dict],
    jd_requirements: dict,
    top_n: Optional[int] = None,
) -> list[dict]:
    """
    Score all candidates and return them sorted by overall_score (descending).

    Args:
        candidates:      List of parsed resume dicts
        jd_requirements: Parsed JD dict
        top_n:           If set, return only the top N candidates

    Returns:
        Sorted list of scoring dicts, each with 'rank' populated (1-indexed).
    """
    print(f"\n  📊 Scoring {len(candidates)} candidate(s)…")

    scored: list[dict] = []
    for idx, candidate in enumerate(candidates, 1):
        name = candidate.get("name", f"Candidate {idx}")
        print(f"  [{idx}/{len(candidates)}] Scoring: {name}")
        try:
            result = score_candidate(candidate, jd_requirements)
            scored.append(result)
        except Exception as exc:
            print(f"    ⚠️  Scoring failed for {name}: {exc}")

    scored.sort(key=lambda x: x["overall_score"], reverse=True)

    for rank, result in enumerate(scored, 1):
        result["rank"] = rank

    return scored[:top_n] if top_n else scored


# ── Recruiter summary generation ──────────────────────────────────────────────

def generate_recruiter_summary(result: dict, jd_requirements: dict) -> str:
    """
    Generate a natural-language recruiter note for the candidate.

    Strategy:
      - LLM summary if API key is present (richer, more natural)
      - Rule-based fallback otherwise (always works)
    """
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            return _llm_summary(result, jd_requirements, api_key)
        except Exception as exc:
            print(f"    ⚠️  LLM summary failed ({exc}). Using rule-based fallback.")
    return _rule_based_summary(result, jd_requirements)


def _llm_summary(result: dict, jd_requirements: dict, api_key: str) -> str:
    """Call an LLM to generate a recruiter note (3–4 sentences)."""
    from openai import OpenAI  # type: ignore

    use_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    base_url = "https://openrouter.ai/api/v1" if use_openrouter else None
    model = os.getenv(
        "OPENROUTER_MODEL",
        "meta-llama/llama-3.3-70b-instruct:free" if use_openrouter else "gpt-3.5-turbo",
    )

    client = OpenAI(api_key=api_key, base_url=base_url)

    matched = ", ".join(result["matched_skills"][:6]) or "None"
    missing = ", ".join(result["missing_skills"][:5]) or "None"

    prompt = (
        f"Write a concise recruiter note (3–4 sentences) for this candidate screening result.\n"
        f"Be professional, specific, and actionable. No bullet points.\n\n"
        f"Role:          {jd_requirements.get('role_title', 'the position')}\n"
        f"Candidate:     {result['candidate']}\n"
        f"Overall Score: {result['overall_score']}/100\n"
        f"Recommendation:{result['recommendation']}\n"
        f"Matched Skills:{matched}\n"
        f"Missing Skills:{missing}\n"
        f"Experience:    {result['experience_years_found']} yr "
        f"(required {result['experience_years_required']} yr)\n"
        f"Education:     {result['education_found']}\n"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=160,
        temperature=0.7,
    )
    return (resp.choices[0].message.content or "").strip()


def _rule_based_summary(result: dict, jd_requirements: dict) -> str:
    """Generate a recruiter note using rules — no API key needed."""
    name  = result["candidate"]
    score = result["overall_score"]
    rec   = result["recommendation"].split("—")[0].strip()
    exp   = result["experience_years_found"]
    req   = result["experience_years_required"]
    edu   = result["education_found"]
    matched = result["matched_skills"][:3]
    missing = result["missing_skills"][:3]

    parts = [f"{name} scored {score:.0f}/100 — {rec}."]

    if matched:
        parts.append(f"Strong in {', '.join(matched)}.")
    if missing:
        parts.append(f"Gap areas: {', '.join(missing)}.")

    if exp >= req:
        parts.append(f"Exceeds experience requirement ({exp} yr vs. {req} yr required).")
    elif exp > 0:
        parts.append(f"Has {exp} yr experience; role requires {req} yr.")
    else:
        parts.append("Experience duration could not be determined from resume.")

    parts.append(f"Education: {edu}.")
    return " ".join(parts)


# ── Recommendation tiers ──────────────────────────────────────────────────────

def _get_recommendation(score: float) -> str:
    if score >= 80:
        return "Strong Match — Interview Recommended"
    elif score >= 65:
        return "Good Match — Consider for Interview"
    elif score >= 50:
        return "Moderate Match — Review Manually"
    else:
        return "Weak Match — Does Not Meet Requirements"
