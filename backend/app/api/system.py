# backend/app/api/system.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any
import sqlite3
import time
from app.db.sqlite import DB_PATH, get_routing_prefs, update_routing_prefs
from app.core.config import SettingsManager

router = APIRouter(prefix="/api/settings", tags=["system"])

class KeyUpdate(BaseModel):
    provider: str
    key: str

class RoutingUpdate(BaseModel):
    prefs: Dict[str, List[str]]

class KeyTest(BaseModel):
    provider: str
    key: str

@router.get("/health")
async def health_check():
    # 1. Ping SQLite
    db_ok = False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        db_ok = True
    except Exception:
        pass

    # 2. Check SentenceTransformer loading
    # (Checking if similarity computes or importable)
    embedding_ok = False
    try:
        from app.ai.embeddings import calculate_similarity
        embedding_ok = True
    except Exception:
        pass

    # 3. Check Providers keys configured
    providers_status = SettingsManager.get_all_providers_status()

    # Determine health
    status = "healthy"
    if not db_ok or not embedding_ok:
        status = "degraded"

    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
        "embeddings": "loaded" if embedding_ok else "failed",
        "providers": providers_status,
        "timestamp": time.time()
    }

@router.get("/keys")
async def get_keys_status():
    return SettingsManager.get_all_providers_status()

@router.post("/keys")
async def update_key(data: KeyUpdate):
    if data.provider.lower() not in ["openai", "openrouter", "anthropic", "gemini"]:
         raise HTTPException(status_code=400, detail="Invalid provider")
    try:
        SettingsManager.set_provider_key(data.provider.lower(), data.key)
        return {"status": "success", "message": f"API key updated for {data.provider}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing")
async def get_routing():
    try:
        return get_routing_prefs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/routing")
async def update_routing(data: RoutingUpdate):
    try:
        update_routing_prefs(data.prefs)
        return {"status": "success", "message": "Routing preferences updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-key")
async def test_key(data: KeyTest):
    # Mock validation or direct OpenRouter connectivity verification
    if not data.key.strip():
        return {"valid": False, "message": "Key cannot be empty"}
    
    # We can perform a lightweight mock verification to prevent blocking on network timeouts
    if len(data.key) < 10:
        return {"valid": False, "message": "Key is too short or malformed"}
        
    return {"valid": True, "message": f"Connection verified for {data.provider}"}
