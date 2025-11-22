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

# CRITICAL: Railway uses this CMD. Do NOT override in railway.toml or UI.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
