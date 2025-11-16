FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ffmpeg && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt
COPY . .
EXPOSE 8000
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
