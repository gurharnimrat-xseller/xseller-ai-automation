# Production Dockerfile for Railway deployment
# Builds and runs the FastAPI backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for video/audio processing
# ffmpeg: video generation and manipulation
# build-essential: compiling Python packages with C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire repository (needed for agents/ directory and guardrails)
COPY . /app

# Install Python dependencies from backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Create output directory for generated content
RUN mkdir -p /app/backend/output

# Expose port 8000 (Railway will map this automatically)
EXPOSE 8000

# Start FastAPI with Uvicorn
# - backend.app.main:app is the FastAPI application instance
# - host 0.0.0.0 allows external connections
# - port from $PORT env var (Railway injects this) or default 8000
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
