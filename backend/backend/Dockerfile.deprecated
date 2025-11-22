FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements file into /app/requirements.txt (from repo root context)
COPY backend/requirements.txt /app/requirements.txt

# Run pip install -r /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# Copy backend source into /app (from repo root context)
COPY backend/app /app/app
COPY agents /app/agents

# Expose port 8000
EXPOSE 8000

# Start FastAPI using uvicorn app.main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
