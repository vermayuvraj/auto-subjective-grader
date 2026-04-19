FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    EASYOCR_USE_GPU=true \
    API_RUNS_ROOT=/app/persistent_data/api_runs \
    TORCH_HOME=/opt/model-cache/torch \
    HF_HOME=/opt/model-cache/huggingface \
    TRANSFORMERS_CACHE=/opt/model-cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/opt/model-cache/sentence-transformers \
    EASYOCR_MODULE_PATH=/opt/model-cache/easyocr

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    fonts-dejavu-core \
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
    pip install --prefer-binary -r requirements.backend.txt && \
    pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu118 \
      torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0

COPY backend_api ./backend_api
COPY src ./src
COPY start-backend.sh ./start-backend.sh

RUN mkdir -p /app/persistent_data/api_runs /opt/model-cache/torch /opt/model-cache/huggingface /opt/model-cache/sentence-transformers /opt/model-cache/easyocr
RUN python backend_api/preload_models.py
RUN sed -i 's/\r$//' /app/start-backend.sh && chmod +x /app/start-backend.sh

EXPOSE 8001

CMD ["sh", "/app/start-backend.sh"]
