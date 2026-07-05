# backend/app/db/sqlite.py
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "screenit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Runs Table (stores campaign runs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        role_title TEXT NOT NULL,
        job_description TEXT NOT NULL,
        processing_time REAL DEFAULT 0.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Candidates Table (stores candidate assessments)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        linkedin TEXT,
        github TEXT,
        overall_score REAL NOT NULL,
        confidence TEXT NOT NULL,
        match_status TEXT NOT NULL,
        scores TEXT NOT NULL,          -- JSON string
        experience_years REAL NOT NULL,
        education_degree TEXT NOT NULL,
        matched_skills TEXT NOT NULL,  -- JSON string
        missing_skills TEXT NOT NULL,  -- JSON string
        why_reasoning TEXT NOT NULL,   -- JSON string
        risk_factors TEXT NOT NULL,    -- JSON string
        recruiter_brief TEXT,
        strengths TEXT,                -- JSON string
        weaknesses TEXT,               -- JSON string
        interview_questions TEXT,      -- JSON string
        raw_profile TEXT,              -- JSON string
        model_used TEXT DEFAULT '',
        latency REAL DEFAULT 0.0,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    )
    """)

    # Try to add model_used and latency columns to candidates if the table already existed without them
    try:
        cursor.execute("ALTER TABLE candidates ADD COLUMN model_used TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE candidates ADD COLUMN latency REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass
    
    # Model Routing Matrix Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routing_prefs (
        task TEXT PRIMARY KEY,
        models_json TEXT NOT NULL
    )
    """)

    # Populate default routing presets if not present
    cursor.execute("SELECT COUNT(*) FROM routing_prefs")
    if cursor.fetchone()[0] == 0:
        defaults = {
            "parsing": ["qwen", "openai", "anthropic", "gemini", "offline"],
            "summary": ["openai", "qwen", "anthropic", "gemini", "offline"],
            "questions": ["anthropic", "openai", "qwen", "gemini", "offline"],
            "default": ["openai", "qwen", "anthropic", "gemini", "offline"]
        }
        for task, cascade in defaults.items():
            cursor.execute("INSERT INTO routing_prefs (task, models_json) VALUES (?, ?)", (task, json.dumps(cascade)))
    
    conn.commit()
    conn.close()

def save_run(run_data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO runs (run_id, role_title, job_description, processing_time) VALUES (?, ?, ?, ?)",
        (run_data["run_id"], run_data["role_title"], run_data["job_description"], run_data.get("processing_time", 0.0))
    )
    conn.commit()
    conn.close()

def save_candidate(cand: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO candidates (
            id, run_id, name, email, phone, linkedin, github, 
            overall_score, confidence, match_status, scores, 
            experience_years, education_degree, matched_skills, 
            missing_skills, why_reasoning, risk_factors, recruiter_brief, 
            strengths, weaknesses, interview_questions, raw_profile,
            model_used, latency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cand["id"],
            cand["run_id"],
            cand["name"],
            cand.get("email"),
            cand.get("phone"),
            cand.get("linkedin"),
            cand.get("github"),
            cand["overall_score"],
            cand["confidence"],
            cand["match_status"],
            json.dumps(cand["scores"]),
            cand["experience_years"],
            cand["education_degree"],
            json.dumps(cand["matched_skills"]),
            json.dumps(cand["missing_skills"]),
            json.dumps(cand["why_reasoning"]),
            json.dumps(cand.get("risk_factors", [])),
            cand.get("recruiter_brief"),
            json.dumps(cand.get("strengths", [])),
            json.dumps(cand.get("weaknesses", [])),
            json.dumps(cand.get("interview_questions", [])),
            json.dumps(cand.get("raw_profile", {})),
            cand.get("model_used", ""),
            cand.get("latency", 0.0)
        )
    )
    conn.commit()
    conn.close()

def get_runs() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.run_id, r.role_title, r.job_description, r.processing_time, r.created_at, 
               (SELECT COUNT(*) FROM candidates WHERE run_id = r.run_id) as candidate_count
        FROM runs r
        ORDER BY r.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_run_details(run_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get run meta
    cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    run_row = cursor.fetchone()
    if not run_row:
        conn.close()
        return None
        
    run_data = dict(run_row)
    
    # Get candidates
    cursor.execute("SELECT * FROM candidates WHERE run_id = ? ORDER BY overall_score DESC", (run_id,))
    cand_rows = cursor.fetchall()
    conn.close()
    
    candidates = []
    for row in cand_rows:
        cand = dict(row)
        # Parse JSON columns
        cand["scores"] = json.loads(cand["scores"])
        cand["matched_skills"] = json.loads(cand["matched_skills"])
        cand["missing_skills"] = json.loads(cand["missing_skills"])
        cand["why_reasoning"] = json.loads(cand["why_reasoning"])
        cand["risk_factors"] = json.loads(cand["risk_factors"])
        cand["strengths"] = json.loads(cand["strengths"])
        cand["weaknesses"] = json.loads(cand["weaknesses"])
        cand["interview_questions"] = json.loads(cand["interview_questions"])
        cand["raw_profile"] = json.loads(cand["raw_profile"])
        candidates.append(cand)
        
    run_data["candidates"] = candidates
    return run_data

def delete_run(run_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_candidate(candidate_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_candidate(candidate_id: str, updates: Dict[str, Any]) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Filter valid columns to update
    valid_cols = ["name", "email", "phone", "linkedin", "github", "overall_score", 
                  "confidence", "match_status", "recruiter_brief", "model_used"]
    
    set_clauses = []
    params = []
    for col, val in updates.items():
        if col in valid_cols:
            set_clauses.append(f"{col} = ?")
            params.append(val)
            
    if not set_clauses:
        conn.close()
        return False
        
    params.append(candidate_id)
    query = f"UPDATE candidates SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, params)
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def get_routing_prefs() -> Dict[str, List[str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT task, models_json FROM routing_prefs")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: json.loads(row[1]) for row in rows}

def update_routing_prefs(prefs: Dict[str, List[str]]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for task, cascade in prefs.items():
        cursor.execute(
            "INSERT OR REPLACE INTO routing_prefs (task, models_json) VALUES (?, ?)",
            (task, json.dumps(cascade))
        )
    conn.commit()
    conn.close()

def get_analytics_dashboard() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Total runs and candidates
    cursor.execute("SELECT COUNT(*) FROM runs")
    total_campaigns = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]
    
    # 2. Avg overall score
    cursor.execute("SELECT AVG(overall_score) FROM candidates")
    avg_score = cursor.fetchone()[0] or 0.0
    
    # 3. Avg experience
    cursor.execute("SELECT AVG(experience_years) FROM candidates")
    avg_experience = cursor.fetchone()[0] or 0.0
    
    # 4. Interview ready candidates (overall_score >= 80)
    cursor.execute("SELECT COUNT(*) FROM candidates WHERE overall_score >= 80")
    interview_ready = cursor.fetchone()[0]
    
    # 5. Avg processing time (runs)
    cursor.execute("SELECT AVG(processing_time) FROM runs")
    avg_processing_time = cursor.fetchone()[0] or 0.0
    
    # 6. Top matched skills and missing skills
    cursor.execute("SELECT matched_skills, missing_skills FROM candidates")
    all_rows = cursor.fetchall()
    
    matched_freq = {}
    missing_freq = {}
    for row in all_rows:
        try:
            m_skills = json.loads(row[0])
            for s in m_skills:
                matched_freq[s] = matched_freq.get(s, 0) + 1
        except Exception:
            pass
            
        try:
            miss_skills = json.loads(row[1])
            for s in miss_skills:
                missing_freq[s] = missing_freq.get(s, 0) + 1
        except Exception:
            pass
            
    top_matched = sorted(matched_freq.items(), key=lambda x: x[1], reverse=True)
    top_missing = sorted(missing_freq.items(), key=lambda x: x[1], reverse=True)
    
    top_skill = top_matched[0][0] if top_matched else "Python"
    most_missing_skill = top_missing[0][0] if top_missing else "Kubernetes"
    
    # 7. Highest ranked candidate
    cursor.execute("SELECT name, overall_score, recruiter_brief FROM candidates ORDER BY overall_score DESC LIMIT 1")
    highest_row = cursor.fetchone()
    highest_candidate = {
        "name": highest_row[0] if highest_row else "No Candidates",
        "score": highest_row[1] if highest_row else 0.0,
        "brief": highest_row[2] if highest_row else "N/A"
    }
    
    conn.close()
    
    return {
        "total_campaigns": total_campaigns,
        "total_candidates": total_candidates,
        "avg_score": round(avg_score, 1),
        "avg_experience": round(avg_experience, 1),
        "interview_ready": interview_ready,
        "avg_processing_time": round(avg_processing_time, 2),
        "top_skill": top_skill,
        "most_missing_skill": most_missing_skill,
        "highest_candidate": highest_candidate
    }

