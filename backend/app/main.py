from agents.checks.router import should_offload, offload_to_gemini  # guardrails
from __future__ import annotations

# CRITICAL: Load .env file FIRST before any other imports that might use environment variables
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging ASAP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🚀 FastAPI Application Starting...")
logger.info("=" * 80)

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
logger.info(f"✅ Environment loaded from: {env_path}")

# Now import everything else (after .env is loaded)
from contextlib import asynccontextmanager
from typing import AsyncIterator

logger.info("📦 Importing FastAPI and dependencies...")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from app.database import engine

logger.info("📦 Importing app modules...")
from app.models import *  # noqa: F401,F403 - import models to register metadata
from app import scheduler
from app.routes import router

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xseller.db")
logger.info(f"🗄️  Database URL: {DATABASE_URL[:30]}...")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: create tables and start scheduler
    logger.info("🔧 Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database tables created")
    
    logger.info("⏰ Starting scheduler...")
    scheduler.start_scheduler()
    logger.info("✅ Scheduler started")
    
    logger.info("=" * 80)
    logger.info("✅ FastAPI Application Ready!")
    logger.info("=" * 80)
    
    try:
        yield
    finally:
        # Shutdown: stop scheduler
        logger.info("🛑 Shutting down scheduler...")
        scheduler.stop_scheduler()
        logger.info("✅ Scheduler stopped")


logger.info("🏗️  Creating FastAPI app instance...")
app = FastAPI(lifespan=lifespan)
logger.info("✅ FastAPI app created")

# CORS: allow localhost:3000 (MUST be added before routers)
# Production: Set ALLOWED_ORIGINS environment variable (comma-separated)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

logger.info(f"🌐 Adding CORS middleware for origins: {ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router with all API endpoints
logger.info("📍 Including API router...")
app.include_router(router)
logger.info("✅ API router included")

# Log all registered routes
logger.info("📋 Registered Routes:")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        logger.info(f"  {', '.join(route.methods):8} {route.path}")
    elif hasattr(route, 'path'):
        logger.info(f"  {'MOUNT':8} {route.path}")
logger.info("=" * 80)

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
