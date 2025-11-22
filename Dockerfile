FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend and agents directories
COPY backend backend
COPY agents agents

# Set PYTHONPATH to include both /app (repo root) and /app/backend
ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

# Use shell form CMD to enable PORT variable expansion
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
