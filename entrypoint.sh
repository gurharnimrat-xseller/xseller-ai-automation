#!/bin/sh
# Entrypoint script for Railway deployment
# This ensures PORT environment variable is properly expanded

# Use Railway's PORT if set, otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT"
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"
