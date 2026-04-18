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
    pip install --index-url https://download.pytorch.org/whl/cu121 \
      torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 && \
    pip install --prefer-binary -r requirements.backend.txt

COPY backend_api ./backend_api
COPY src ./src
COPY start-backend.sh ./start-backend.sh

RUN mkdir -p /app/persistent_data/api_runs /opt/model-cache/torch /opt/model-cache/huggingface /opt/model-cache/sentence-transformers /opt/model-cache/easyocr
RUN python - <<'PY'
import os

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
import easyocr
from pix2tex.cli import LatexOCR

SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
easyocr.Reader(["en"], gpu=False)
LatexOCR()
PY
RUN sed -i 's/\r$//' /app/start-backend.sh && chmod +x /app/start-backend.sh

EXPOSE 8001

CMD ["sh", "/app/start-backend.sh"]
