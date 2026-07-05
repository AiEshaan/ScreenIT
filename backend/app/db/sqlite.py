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
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    )
    """)
    
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
            strengths, weaknesses, interview_questions, raw_profile
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            json.dumps(cand.get("raw_profile", {}))
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
