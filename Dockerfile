FROM python:3.11-slim

# Work inside /app
WORKDIR /app

# Copy backend requirements into the image
COPY backend/requirements.txt ./requirements.txt

# Install system deps + Python deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ffmpeg && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

# Copy the whole repo (backend + agents + everything)
COPY . /app

# Expose port (Railway maps this)
EXPOSE 8000

# Start the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
