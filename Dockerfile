FROM python:3.11-slim

# Work inside /app
WORKDIR /app

# Copy whole repo (backend + agents + everything)
COPY . /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Expose port
EXPOSE 8000

# Start the backend
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
