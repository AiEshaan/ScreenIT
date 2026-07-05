# backend/app/api/screening.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
import tempfile

from app.services.screening_service import AIEngine
from app.db.sqlite import init_db, save_run, save_candidate, get_runs, get_run_details, get_analytics_dashboard, delete_run, delete_candidate, update_candidate
from app.api.system import router as system_router

app = FastAPI(title="ScreenIt API", description="AI Resume Screening Platform Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)

engine = AIEngine()

# Initialize Database on app startup
init_db()

@app.post("/api/screen")
async def screen_resumes(
    role_title: str = Form(""),
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    if not resumes:
        raise HTTPException(status_code=400, detail="Please upload at least one resume file")
        
    temp_files = []
    try:
        # Prepare resumes as byte lists or text strings
        resumes_payload = []
        for file in resumes:
            content = await file.read()
            # Try decoding as text, fallback to empty string
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                # If binary PDF or other formats, we write to a temporary file for parsing
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
                    temp.write(content)
                    temp_path = temp.name
                    temp_files.append(temp_path)
                text_content = temp_path # Send temp file path as reference (parse_resume handles paths)

            resumes_payload.append({
                "filename": file.filename,
                "content": text_content
            })
            
        # Screen candidates using AI Engine
        result = engine.process_screening(job_description, role_title, resumes_payload)
        
        # Persist to SQLite
        save_run(result)
        for cand in result["candidates"]:
            save_candidate(cand)
            
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)

@app.get("/api/runs")
async def get_all_runs():
    try:
        return get_runs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    details = get_run_details(run_id)
    if not details:
        raise HTTPException(status_code=404, detail="Campaign run not found")
    return details

@app.get("/api/analytics")
async def get_analytics():
    try:
        return get_analytics_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/runs/{run_id}")
async def remove_run(run_id: str):
    success = delete_run(run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"status": "success", "message": f"Run {run_id} deleted successfully"}

@app.delete("/api/candidates/{candidate_id}")
async def remove_candidate(candidate_id: str):
    success = delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "success", "message": f"Candidate {candidate_id} deleted successfully"}

@app.patch("/api/candidates/{candidate_id}")
async def patch_candidate(candidate_id: str, updates: dict):
    success = update_candidate(candidate_id, updates)
    if not success:
         raise HTTPException(status_code=400, detail="Failed to update candidate or no updates provided")
    return {"status": "success", "message": f"Candidate {candidate_id} updated successfully"}


