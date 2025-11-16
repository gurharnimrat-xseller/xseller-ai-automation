from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # guardrails

# CRITICAL: Load .env file FIRST before any other imports that might use environment variables
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Now import everything else (after .env is loaded)
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from app.database import engine

from app.models import *  # noqa: F401,F403 - import models to register metadata
from app import scheduler
from app.routes import router

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xseller.db")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: create tables and start scheduler
    SQLModel.metadata.create_all(engine)
    scheduler.start_scheduler()
    try:
        yield
    finally:
        # Shutdown: stop scheduler
        scheduler.stop_scheduler()


app = FastAPI(lifespan=lifespan)  # v1.1.0 - BackgroundTasks fix deployed

# CORS: allow localhost:3000 (MUST be added before routers)
# Production: Set ALLOWED_ORIGINS environment variable (comma-separated)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router with all API endpoints
app.include_router(router)

# Mount static files for serving videos and other output
output_dir = Path(__file__).parent.parent / "output"
output_dir.mkdir(exist_ok=True)
app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")


@app.get("/")
async def root():
    return {"message": "Xseller.ai API", "status": "running"}


@app.get("/api/health")
async def health():
    database_status = "connected"
    try:
        # Simple connectivity check
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
    except Exception:
        database_status = "error"

    scheduler_status = "running" if scheduler.is_running() else "stopped"
    return {"api": "healthy", "database": database_status, "scheduler": scheduler_status}


# Allow running via: python -m app.main
if __name__ == "__main__":
    import uvicorn

    # Read port from environment (default 8000)
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
