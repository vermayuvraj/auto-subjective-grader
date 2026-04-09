#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8001}"

echo "Starting FastAPI backend on port ${PORT_VALUE}"
echo "API_RUNS_ROOT=${API_RUNS_ROOT:-unset}"

exec python -m uvicorn backend_api.main:app \
  --host 0.0.0.0 \
  --port "${PORT_VALUE}" \
  --workers 1
