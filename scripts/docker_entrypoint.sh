#!/bin/sh
set -e

echo "[Applymize] Running migrations..."
alembic upgrade head

if [ "${AUTO_SEED}" = "true" ]; then
  echo "[Applymize] Running demo seed..."
  python scripts/dev_seed.py || true
fi

echo "[Applymize] Starting API..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
