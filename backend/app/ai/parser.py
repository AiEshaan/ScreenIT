"""
resume_screening/parser.py
---------------------------
Resume text extraction and structured parsing.

Strategy (reliability-first):
  1. PDF/TXT  →  raw text  (PyMuPDF — fast, handles complex layouts)
  2. Regex + rule-based extraction  (always works, zero dependencies)
  3. LLM enhancement  (optional — only if API key is set in environment)

Design rationale:
  Inverting the LLM-first approach means evaluators and reviewers can run
  the project without any API key.  The LLM layer adds polish when available
  but is never a hard requirement.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

# PyMuPDF — best-in-class PDF text extraction
try:
    import fitz  # type: ignore
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from app.ai.skills_database import extract_skills


# ── Public API ────────────────────────────────────────────────────────────────

def extract_text(file_path: str) -> str:
    """
    Extract raw text from a PDF or plain-text resume file.

    Supports: .pdf, .txt, .md
    Raises ValueError for unsupported formats.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for PDF parsing.\n"
                "Install it with: pip install PyMuPDF"
            )
        with fitz.open(str(path)) as doc:
            pages = [page.get_text("text") for page in doc]
        return "\n".join(pages)

    raise ValueError(f"Unsupported resume format: {suffix!r}. Use .pdf or .txt")


def parse_resume(text: str, filename: str = "", use_llm: bool = True) -> dict:
    """
    Parse raw resume text into a structured profile dictionary.

    Returns:
        {
          name, email, phone, linkedin, github, summary,
          skills, experience, education, raw_text
        }

    Parsing strategy:
      Step 1 — Regex extraction (always runs, no API needed)
      Step 2 — LLM enhancement (runs only when OPENROUTER_API_KEY or
                OPENAI_API_KEY is set in environment)
    """
    # Step 1: deterministic regex parse
    profile = _regex_parse(text, filename)

    # Step 2: optional LLM enhancement
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if use_llm and api_key:
        try:
            profile = _llm_enhance(text, profile, api_key)
        except Exception as exc:
            # Non-fatal — regex result is still usable
            print(f"    ⚠️  LLM enhancement skipped: {exc}")

    profile["raw_text"] = text
    return profile


# ── Regex-based parsing ───────────────────────────────────────────────────────

def _regex_parse(text: str, filename: str = "") -> dict:
    """Rule-based resume parser.  Requires no external services."""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    return {
        "name": _extract_name(lines, filename),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "linkedin": _extract_pattern(text, r"linkedin\.com/in/[\w\-]+", "https://"),
        "github": _extract_pattern(text, r"github\.com/[\w\-]+", "https://"),
        "summary": _extract_section(text, ["SUMMARY", "OBJECTIVE", "PROFILE", "ABOUT ME"]),
        "skills": extract_skills(text),
        "experience": _extract_experience(text),
        "education": _extract_education(text),
    }


def _extract_name(lines: list[str], filename: str) -> str:
    """Heuristic: first short line made of letters/spaces near the top."""
    for line in lines[:6]:
        # 2–5 words, no digits, reasonable length
        if re.match(r"^[A-Za-z][A-Za-z\s\-\.]{3,50}$", line):
            word_count = len(line.split())
            if 2 <= word_count <= 5:
                return line
    # Fallback: derive from filename
    if filename:
        stem = Path(filename).stem.replace("_", " ").replace("-", " ")
        return stem.title()
    return "Unknown Candidate"


def _extract_email(text: str) -> str:
    m = re.search(r"[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    m = re.search(r"[\+\(]?[\d][\d\s\-\(\)\.]{8,15}[\d]", text)
    return m.group(0).strip() if m else ""


def _extract_pattern(text: str, pattern: str, prefix: str = "") -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return f"{prefix}{m.group(0)}" if m else ""


def _extract_section(text: str, headers: list[str], end_headers: Optional[list[str]] = None) -> str:
    """
    Extract the first N lines of a named resume section.
    Stops at the next section header.
    """
    if end_headers is None:
        end_headers = [
            "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS",
            "CERTIFICATIONS", "AWARDS", "WORK HISTORY",
        ]

    header_rx = re.compile(
        r"^\s*(?:" + "|".join(re.escape(h) for h in headers) + r")\s*$",
        re.IGNORECASE,
    )
    end_rx = re.compile(
        r"^\s*(?:" + "|".join(re.escape(h) for h in end_headers) + r")\s*$",
        re.IGNORECASE,
    )

    lines = text.split("\n")
    capturing = False
    collected: list[str] = []

    for line in lines:
        stripped = line.strip()
        if header_rx.match(stripped):
            capturing = True
            continue
        if capturing and end_rx.match(stripped):
            break
        if capturing and stripped:
            collected.append(stripped)
        if len(collected) >= 5:  # cap at 5 lines for summary
            break

    return " ".join(collected)


def _extract_experience(text: str) -> list[dict]:
    """Extract work-experience entries with date ranges."""
    section = _get_section_text(
        text,
        start_patterns=["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "CAREER"],
        end_patterns=["EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS"],
    )
    if not section:
        return []

    # Date range pattern — handles Month YYYY, YYYY, and "Present"
    date_rx = re.compile(
        r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)\.?\s*\d{4}|\d{4})"
        r"\s*[-–—to]+\s*"
        r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)\.?\s*\d{4}|\d{4}|Present|Current|Now)",
        re.IGNORECASE,
    )

    entries: list[dict] = []
    current: Optional[dict] = None

    for line in section.split("\n"):
        line = line.strip()
        if not line:
            continue

        date_m = date_rx.search(line)
        if date_m:
            if current:
                entries.append(current)
            title_part = line[: date_m.start()].strip()
            current = {
                "title": title_part or "Engineer",
                "company": "",
                "start": date_m.group(1),
                "end": date_m.group(2),
                "bullets": [],
            }
        elif current:
            if line.startswith(("•", "-", "*", "·", "▪", "◦", "–")):
                current["bullets"].append(line.lstrip("•-*·▪◦– "))
            elif not current["company"] and len(line) < 80 and not re.match(r"^\d", line):
                current["company"] = line

    if current:
        entries.append(current)

    return entries


def _extract_education(text: str) -> list[dict]:
    """Extract education entries, normalizing degree text."""
    section = _get_section_text(
        text,
        start_patterns=["EDUCATION", "ACADEMIC", "QUALIFICATION"],
        end_patterns=["EXPERIENCE", "SKILLS", "PROJECTS", "CERTIFICATIONS", "WORK"],
    )
    if not section:
        # Try scanning the whole document for degree keywords
        section = text

    degree_rx = re.compile(
        r"\b(Ph\.?D\.?|Doctor(?:ate)?(?: of \w+)*"
        r"|M\.?(?:Tech|E|S|Sc|BA|CA|Eng)\.?"
        r"|Master(?:s)?(?: of [A-Za-z\s]+)?"
        r"|MBA|M\.?B\.?A"
        r"|B\.?(?:Tech|E|S|Sc|CA|Com|Eng)\.?"
        r"|Bachelor(?:s)?(?: of [A-Za-z\s]+)?"
        r"|BE|BTech|BSc|BCA|BBA"
        r"|Diploma|Associate(?:s)?(?:\'s)?)\b",
        re.IGNORECASE,
    )

    entries: list[dict] = []
    seen: set[str] = set()

    for line in section.split("\n"):
        line = line.strip()
        if not line or line in seen:
            continue
        if degree_rx.search(line):
            seen.add(line)
            year_m = re.search(r"\b(20\d{2}|19\d{2})\b", line)
            entries.append({
                "degree": line[:120],
                "school": "",
                "year": year_m.group(0) if year_m else "",
            })

    return entries[:4]  # cap at 4 to avoid noise


def _get_section_text(text: str, start_patterns: list[str], end_patterns: list[str]) -> str:
    """Return the raw text of a named section."""
    start_rx = re.compile(
        r"^\s*(?:" + "|".join(re.escape(p) for p in start_patterns) + r")\s*$",
        re.IGNORECASE,
    )
    end_rx = re.compile(
        r"^\s*(?:" + "|".join(re.escape(p) for p in end_patterns) + r")\s*$",
        re.IGNORECASE,
    )

    lines = text.split("\n")
    capturing = False
    section: list[str] = []

    for line in lines:
        if start_rx.match(line.strip()):
            capturing = True
            continue
        if capturing and end_rx.match(line.strip()):
            break
        if capturing:
            section.append(line)

    return "\n".join(section)


# ── LLM enhancement (optional) ────────────────────────────────────────────────

def _llm_enhance(text: str, base: dict, api_key: str) -> dict:
    """
    Use an LLM to improve the regex-parsed profile.
    Merges LLM output with regex output — skills list uses union of both.
    """
    from openai import OpenAI  # type: ignore

    use_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    base_url = "https://openrouter.ai/api/v1" if use_openrouter else None
    model = os.getenv(
        "OPENROUTER_MODEL",
        "meta-llama/llama-3.3-70b-instruct:free" if use_openrouter else "gpt-3.5-turbo",
    )

    client = OpenAI(api_key=api_key, base_url=base_url)

    prompt = (
        "Parse this resume. Return ONLY valid JSON with these keys:\n"
        '{"name":"","email":"","summary":"","skills":[],"experience":['
        '{"company":"","title":"","start":"","end":"","bullets":[]}],'
        '"education":[{"school":"","degree":"","year":""}]}\n\n'
        f"RESUME:\n{text[:5000]}"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0,
    )
    raw = resp.choices[0].message.content or ""

    # Extract JSON block from response
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return base

    parsed = json.loads(m.group(0))

    # Merge: prefer LLM for structure fields, union for skills
    base.update({
        "name": parsed.get("name") or base["name"],
        "email": parsed.get("email") or base["email"],
        "summary": parsed.get("summary") or base["summary"],
        "experience": parsed.get("experience") or base["experience"],
        "education": parsed.get("education") or base["education"],
    })

    llm_skills = parsed.get("skills", [])
    base["skills"] = sorted(set(base["skills"]) | set(llm_skills))

    return base
