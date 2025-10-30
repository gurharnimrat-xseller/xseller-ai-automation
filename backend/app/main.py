from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.database import engine

from app.models import *  # noqa: F401,F403 - import models to register metadata
from app import scheduler
from app.routes import router


DATABASE_URL = "sqlite:///./xseller.db"


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


app = FastAPI(lifespan=lifespan)

# CORS: allow localhost:3000 (MUST be added before routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router with all API endpoints
app.include_router(router)


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
