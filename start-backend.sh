#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8001}"

echo "Starting FastAPI backend on port ${PORT_VALUE}"
python - <<'PY'
try:
    import torch
    print(
        "Torch runtime:",
        getattr(torch, "__version__", "unknown"),
        "| CUDA available:",
        bool(torch.cuda.is_available()),
        "| Device:",
        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only",
    )
except Exception as exc:
    print("Torch runtime check failed:", exc)
PY

exec python -m uvicorn backend_api.main:app \
  --host 0.0.0.0 \
  --port "${PORT_VALUE}" \
  --workers 1
