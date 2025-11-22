FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend and agents directories
COPY backend backend
COPY agents agents

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set PYTHONPATH to include both /app (repo root) and /app/backend
ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

# Use entrypoint script to properly expand Railway's PORT env var
ENTRYPOINT ["/app/entrypoint.sh"]
