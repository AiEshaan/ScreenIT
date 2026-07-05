"""
resume_screening/similarity.py
--------------------------------
Semantic similarity scoring using SentenceTransformer embeddings.

ML Model: sentence-transformers/all-MiniLM-L6-v2
  - Pretrained transformer (this IS the ML component of the system)
  - ~80 MB, runs fully offline after first download
  - Industry-standard for semantic text similarity tasks
  - No labeled training data required — it's a pretrained model

Design:
  - Lazy-loads the model on first call (avoids cold-start cost at import)
  - Cosine similarity of sentence embeddings → 0–100 scale
  - Skill match uses set intersection (deterministic, fast)
  - Experience and education scores use calibrated formulas
"""

from __future__ import annotations

from typing import List, Optional
import numpy as np

_model = None  # lazy singleton


def _get_model():
    """Load SentenceTransformer model on first use (cached globally)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError:
            raise ImportError(
                "sentence-transformers is required.\n"
                "Install with: pip install sentence-transformers"
            )
        print(
            "  📦 Loading SentenceTransformer (all-MiniLM-L6-v2)…\n"
            "     First run downloads ~80 MB — subsequent runs are instant."
        )
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("  ✅ Model ready.")
    return _model


# ── Semantic similarity ───────────────────────────────────────────────────────

def compute_semantic_similarity(jd_text: str, resume_text: str) -> float:
    """
    Compute semantic similarity between job description and resume.

    Uses cosine similarity of sentence embeddings produced by
    all-MiniLM-L6-v2.  The model understands synonyms and paraphrases —
    e.g., "data wrangling" ↔ "data preprocessing" — unlike keyword matching.

    Returns:
        Score 0–100 (float, 2 decimal places)
    """
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

    model = _get_model()

    jd_clean = _clean_text(jd_text)[:2500]
    resume_clean = _clean_text(resume_text)[:3500]

    embeddings = model.encode([jd_clean, resume_clean], show_progress_bar=False)
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    # Cosine similarity range is typically 0.2–0.9 for dissimilar/similar text.
    # Rescale to 0–100 for interpretability.
    return round(float(sim) * 100, 2)


# ── Skill match ───────────────────────────────────────────────────────────────

def compute_skill_match(
    jd_skills: List[str],
    resume_skills: List[str],
) -> dict:
    """
    Compute the overlap between JD-required skills and candidate skills.

    Returns:
        {
          matched: [...],  # skills from JD found in resume
          missing: [...],  # skills from JD NOT in resume
          score:   float   # 0–100 percentage
        }
    """
    if not jd_skills:
        return {"matched": [], "missing": [], "score": 100.0}

    jd_lower = {s.lower() for s in jd_skills}
    resume_lower = {s.lower() for s in resume_skills}

    matched = [s for s in jd_skills if s.lower() in resume_lower]
    missing = [s for s in jd_skills if s.lower() not in resume_lower]
    score = (len(matched) / len(jd_skills)) * 100

    return {
        "matched": matched,
        "missing": missing,
        "score": round(score, 2),
    }


# ── Experience scoring ────────────────────────────────────────────────────────

def compute_experience_score(candidate_years: float, required_years: float) -> float:
    """
    Score a candidate's experience against the JD requirement.

    Scoring curve:
      candidate ≥ required  →  70–100 (bonus for excess experience, capped at 100)
      candidate < required  →  0–70   (linear partial credit)

    Returns score 0–100.
    """
    if required_years <= 0:
        return 100.0

    ratio = candidate_years / required_years

    if ratio >= 1.0:
        # Meets or exceeds: 70 base + up to 30 bonus for extra experience
        score = 70.0 + min(30.0, (ratio - 1.0) * 20.0)
    else:
        # Partial credit: linear scale 0 → 70
        score = ratio * 70.0

    return round(min(100.0, score), 2)


# ── Education scoring ─────────────────────────────────────────────────────────

def compute_education_score(candidate_level: int, required_level: int) -> float:
    """
    Score candidate's education vs. JD requirement.

    Level encoding:  0=HighSchool, 1=Diploma, 2=Bachelor's, 3=Master's, 4=PhD

    Returns score 0–100.
    """
    if candidate_level < 0:
        return 0.0
    delta = candidate_level - required_level

    if delta >= 0:
        return 100.0          # meets or exceeds
    elif delta == -1:
        return 65.0           # one level below (e.g., diploma vs bachelor's)
    elif delta == -2:
        return 35.0
    else:
        return 10.0           # far below requirement


# ── Utilities ─────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalise whitespace and remove noise characters."""
    import re
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\.,\-\+\#\/\(\)]", " ", text)
    return text.strip()
