FROM python:3.11-slim

# Create working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy ALL repo code (including agents/, backend/, app/)
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
 && pip install -r backend/requirements.txt

# Expose port for Railway
EXPOSE 8000

# Start FastAPI backend
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
