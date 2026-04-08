FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    EASYOCR_USE_GPU=false \
    API_RUNS_ROOT=/app/persistent_data/api_runs

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY README.md ./README.md
COPY rubric.json ./rubric.json
COPY requirements.backend.txt ./requirements.backend.txt
RUN python -m pip install --upgrade "pip<24.1" setuptools wheel && \
    pip install --prefer-binary -r requirements.backend.txt

COPY backend_api ./backend_api
COPY src ./src
COPY start-backend.sh ./start-backend.sh

RUN mkdir -p /app/persistent_data/api_runs
RUN chmod +x /app/start-backend.sh

EXPOSE 8001

CMD ["/app/start-backend.sh"]
