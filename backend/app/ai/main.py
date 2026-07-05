#!/usr/bin/env python3
"""
resume_screening/main.py
--------------------------
CLI entry point for the Resume Screening Agent.

Usage:
    python -m resume_screening.main \\
        --jd sample_data/job_description.txt \\
        --resumes sample_data/resumes/ \\
        --output output/ \\
        [--top-n 5] \\
        [--no-llm-summary]

Outputs:
    output/ranked_candidates_<timestamp>.json
    output/ranked_candidates_<timestamp>.csv
    output/candidate_report_<timestamp>.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from tabulate import tabulate  # type: ignore
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

try:
    from colorama import Fore, Style, init as colorama_init  # type: ignore
    colorama_init(autoreset=True)
    C = True
except ImportError:
    C = False
    class _NoColor:          # minimal shim so f-strings don't break
        def __getattr__(self, _): return ""
    Fore = Style = _NoColor()

from backend.app.ai.parser import extract_text, parse_resume
from backend.app.ai.extractor import extract_jd_requirements
from backend.app.ai.ranking import rank_candidates, generate_recruiter_summary


# ── Banner ────────────────────────────────────────────────────────────────────

BANNER = f"""\
{Fore.CYAN}
╔══════════════════════════════════════════════════════════╗
║   🤖  Resume Screening Agent  v1.0                      ║
║   Powered by SentenceTransformer + Explainable Ranking  ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""


# ── Resume loading ────────────────────────────────────────────────────────────

def load_resumes(resumes_path: str, use_llm: bool = True) -> list[dict]:
    """Parse all .pdf and .txt resumes from a path (file or folder)."""
    path = Path(resumes_path)

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted(path.glob("*.pdf")) + sorted(path.glob("*.txt"))
    else:
        print(f"{Fore.RED}❌ Path not found: {resumes_path}{Style.RESET_ALL}")
        sys.exit(1)

    if not files:
        print(f"{Fore.RED}❌ No PDF or TXT files found in: {resumes_path}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.GREEN}📂 Found {len(files)} resume(s){Style.RESET_ALL}")

    candidates: list[dict] = []
    for idx, f in enumerate(files, 1):
        print(f"  [{idx}/{len(files)}] Parsing: {f.name}")
        try:
            text    = extract_text(str(f))
            profile = parse_resume(text, filename=f.name, use_llm=use_llm)
            profile["filename"] = f.name
            profile["raw_text"] = text
            skill_count = len(profile.get("skills", []))
            print(
                f"    ✅  {profile.get('name', f.stem)}"
                f" | {skill_count} skills"
                f" | {len(profile.get('experience', []))} role(s)"
            )
            candidates.append(profile)
        except Exception as exc:
            print(f"    ❌  Failed to parse {f.name}: {exc}")

    return candidates


# ── Output generation ─────────────────────────────────────────────────────────

def save_outputs(ranked: list[dict], jd_requirements: dict, output_dir: str) -> None:
    """Write JSON, CSV, and Markdown outputs to disk."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON ─────────────────────────────────────────────────────────────────────
    json_path = out / f"ranked_candidates_{ts}.json"
    payload = {
        "generated_at": ts,
        "total_candidates": len(ranked),
        "candidates": ranked,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  💾 JSON   → {json_path}")

    # CSV ──────────────────────────────────────────────────────────────────────
    csv_path = out / f"ranked_candidates_{ts}.csv"
    rows = [
        {
            "Rank":               r["rank"],
            "Candidate":          r["candidate"],
            "File":               r["file"],
            "Overall Score":      r["overall_score"],
            "Recommendation":     r["recommendation"],
            "Semantic Sim.":      r["breakdown"]["semantic_similarity"],
            "Skill Match %":      r["breakdown"]["skill_match"],
            "Experience Score":   r["breakdown"]["experience_match"],
            "Education Score":    r["breakdown"]["education_match"],
            "Experience (yr)":    r["experience_years_found"],
            "Education":          r["education_found"],
            "Matched Skills":     ", ".join(r["matched_skills"][:8]),
            "Missing Skills":     ", ".join(r["missing_skills"][:8]),
            "Recruiter Notes":    r.get("recruiter_notes", ""),
        }
        for r in ranked
    ]
    if PANDAS_AVAILABLE:
        import pandas as pd
        pd.DataFrame(rows).to_csv(csv_path, index=False)
    else:
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    print(f"  💾 CSV    → {csv_path}")

    # Markdown report ──────────────────────────────────────────────────────────
    md_path = out / f"candidate_report_{ts}.md"
    _write_markdown_report(ranked, jd_requirements, md_path)
    print(f"  💾 Report → {md_path}")


def _write_markdown_report(
    ranked: list[dict],
    jd_req: dict,
    path: Path,
) -> None:
    """Write a polished Markdown screening report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    req_skills_str = ", ".join(jd_req.get("required_skills", [])[:12]) or "—"

    lines: list[str] = [
        "# 🤖 Resume Screening Report",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Generated** | {now} |",
        f"| **Role** | {jd_req.get('role_title', '—')} |",
        f"| **Candidates Screened** | {len(ranked)} |",
        f"| **Required Skills** | {req_skills_str} |",
        f"| **Required Experience** | {jd_req.get('required_years', '—')} year(s) |",
        f"| **Required Education** | {jd_req.get('required_education_label', '—')} |",
        "",
        "---",
        "",
        "## Ranked Candidates",
        "",
    ]

    for r in ranked:
        score = r["overall_score"]
        badge = "🟢" if score >= 80 else "🟡" if score >= 65 else "🟠" if score >= 50 else "🔴"

        lines += [
            f"### {badge} Rank #{r['rank']} — {r['candidate']}",
            "",
            f"**Overall Score: `{score}/100`** &nbsp;|&nbsp; **{r['recommendation']}**",
            "",
            "| Dimension | Score | Weight |",
            "|-----------|------:|-------:|",
            f"| 🧠 Semantic Similarity | {r['breakdown']['semantic_similarity']:.1f}% | 50% |",
            f"| 🎯 Skill Match | {r['breakdown']['skill_match']:.1f}% | 25% |",
            f"| 💼 Experience Match | {r['breakdown']['experience_match']:.1f}% | 15% |",
            f"| 🎓 Education Match | {r['breakdown']['education_match']:.1f}% | 10% |",
            "",
            f"**✅ Matched Skills:** {', '.join(r['matched_skills'][:10]) or '_None_'}",
            "",
            f"**❌ Missing Skills:** {', '.join(r['missing_skills'][:10]) or '_None_'}",
            "",
            (
                f"**💼 Experience:** {r['experience_years_found']} yr found "
                f"/ {r['experience_years_required']} yr required"
            ),
            "",
            f"**🎓 Education:** {r['education_found']}",
            "",
        ]

        notes = r.get("recruiter_notes", "")
        if notes:
            lines += [f"> 💬 **Recruiter Note:** {notes}", ""]

        lines += ["---", ""]

    path.write_text("\n".join(lines), encoding="utf-8")


# ── Terminal display ──────────────────────────────────────────────────────────

def print_results(ranked: list[dict]) -> None:
    """Print the ranked candidates table and detailed breakdowns."""
    print(f"\n{Fore.CYAN}{'═' * 68}")
    print("  SCREENING RESULTS")
    print(f"{'═' * 68}{Style.RESET_ALL}\n")

    # Summary table
    table_rows = []
    for r in ranked:
        score = r["overall_score"]
        clr = Fore.GREEN if score >= 80 else Fore.YELLOW if score >= 65 else Fore.RED
        table_rows.append([
            f"#{r['rank']}",
            r["candidate"][:22],
            f"{clr}{score:.1f}{Style.RESET_ALL}",
            r["recommendation"].split("—")[0].strip(),
            f"{r['breakdown']['semantic_similarity']:.0f}%",
            f"{r['breakdown']['skill_match']:.0f}%",
            f"{r['experience_years_found']}yr",
            r["education_found"][:18],
        ])

    headers = ["Rank", "Candidate", "Score", "Result", "Semantic", "Skills", "Exp.", "Education"]

    if TABULATE_AVAILABLE:
        print(tabulate(table_rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # Plain fallback
        print("  " + "  ".join(headers))
        print("  " + "-" * 60)
        for row in table_rows:
            print("  " + "  ".join(str(c) for c in row))

    # Detailed per-candidate breakdown
    print(f"\n{Fore.CYAN}{'─' * 68}{Style.RESET_ALL}")
    for r in ranked:
        score = r["overall_score"]
        clr = Fore.GREEN if score >= 80 else Fore.YELLOW if score >= 65 else Fore.RED
        print(
            f"\n{Style.BRIGHT}#{r['rank']} {r['candidate']}{Style.RESET_ALL}"
            f"  {clr}{score}/100{Style.RESET_ALL}  |  {r['recommendation']}"
        )
        matched_str = ", ".join(r["matched_skills"][:6]) or "None"
        missing_str = ", ".join(r["missing_skills"][:6]) or "None"
        print(f"   ✅ Matched Skills  : {matched_str}")
        print(f"   ❌ Missing Skills  : {missing_str}")
        print(
            f"   💼 Experience      : {r['experience_years_found']} yr found"
            f" / {r['experience_years_required']} yr required"
        )
        print(f"   🎓 Education       : {r['education_found']}")
        notes = r.get("recruiter_notes", "")
        if notes:
            # Word-wrap long notes at 65 chars
            words = notes.split()
            line, wrapped = [], []
            for w in words:
                line.append(w)
                if len(" ".join(line)) > 65:
                    wrapped.append(" ".join(line[:-1]))
                    line = [w]
            if line:
                wrapped.append(" ".join(line))
            print(f"   💬 Recruiter Note  : {wrapped[0]}")
            for cont in wrapped[1:]:
                print(f"                      {cont}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(BANNER)

    parser = argparse.ArgumentParser(
        prog="resume-screening-agent",
        description="AI Resume Screening Agent — rank candidates against a job description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m resume_screening.main \\\n"
            "      --jd sample_data/job_description.txt \\\n"
            "      --resumes sample_data/resumes/\n\n"
            "  python -m resume_screening.main \\\n"
            "      --jd jd.txt --resumes resumes/ --top-n 3 --output results/"
        ),
    )
    parser.add_argument("--jd",            required=True, help="Job description file (.txt)")
    parser.add_argument("--resumes",       required=True, help="Resume folder or single file (.pdf / .txt)")
    parser.add_argument("--output",        default="output", help="Output directory (default: output/)")
    parser.add_argument("--top-n",         type=int, default=None, help="Show only top N ranked candidates")
    parser.add_argument("--no-llm-summary",action="store_true",  help="Skip LLM recruiter summary generation")
    parser.add_argument("--no-llm-parse",  action="store_true",  help="Skip LLM resume parsing enhancement")
    args = parser.parse_args()

    # Load .env if present
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except ImportError:
        pass

    # ── Step 1: Load job description ─────────────────────────────────────────
    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"{Fore.RED}❌ JD file not found: {args.jd}{Style.RESET_ALL}")
        sys.exit(1)

    jd_text = jd_path.read_text(encoding="utf-8")
    print(f"\n{Fore.GREEN}📄 Job Description: {jd_path.name}{Style.RESET_ALL}")

    print("  🔍 Parsing JD requirements…")
    jd_requirements = extract_jd_requirements(jd_text)
    print(
        f"  ✅  {len(jd_requirements['required_skills'])} skills detected"
        f" | {jd_requirements['required_years']} yr required"
        f" | {jd_requirements['required_education_label']} required"
    )

    # ── Step 2: Parse resumes ─────────────────────────────────────────────────
    candidates = load_resumes(args.resumes, use_llm=not args.no_llm_parse)

    if not candidates:
        print(f"{Fore.RED}❌ No resumes could be parsed. Exiting.{Style.RESET_ALL}")
        sys.exit(1)

    # ── Step 3: Rank candidates ───────────────────────────────────────────────
    ranked = rank_candidates(candidates, jd_requirements, top_n=args.top_n)

    # ── Step 4: Generate recruiter notes ─────────────────────────────────────
    if not args.no_llm_summary:
        api_key = (
            __import__("os").getenv("OPENROUTER_API_KEY")
            or __import__("os").getenv("OPENAI_API_KEY")
        )
        src = "LLM" if api_key else "rule-based"
        print(f"\n  💬 Generating recruiter notes ({src})…")
        for r in ranked:
            r["recruiter_notes"] = generate_recruiter_summary(r, jd_requirements)

    # ── Step 5: Display results ───────────────────────────────────────────────
    print_results(ranked)

    # ── Step 6: Save outputs ──────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}💾 Saving outputs to: {args.output}/{Style.RESET_ALL}")
    save_outputs(ranked, jd_requirements, args.output)

    top = ranked[0] if ranked else None
    if top:
        print(
            f"\n{Fore.GREEN}🏆 Top candidate: {top['candidate']}"
            f" ({top['overall_score']}/100){Style.RESET_ALL}"
        )
    print(f"{Fore.GREEN}✅ Done — screened {len(ranked)} candidate(s).{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
