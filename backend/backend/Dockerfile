FROM python:3.11-slim

# Create working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt /app/requirements.txt

# Install Python deps
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy backend source code
COPY backend /app

# Expose port Railway expects
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
