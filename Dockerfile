FROM python:3.11-slim

# MAGIC_DOCKERFILE_TEST_LINE

# Work inside /app
WORKDIR /app

# Copy requirements and install packages
COPY backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the whole repo (backend + agents + everything)
COPY . /app

# Expose port (Railway maps this)
EXPOSE 8000

# Start the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
