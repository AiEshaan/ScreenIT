# backend/main.py
import uvicorn
import os
from dotenv import load_dotenv

from backend.app.api.screening import app

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting ScreenIt Backend on port {port}...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)
