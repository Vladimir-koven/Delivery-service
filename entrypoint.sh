#!/usr/bin/env bash
set -e

echo "[entrypoint] Applying database migrations..."
alembic upgrade head

echo "[entrypoint] Starting uvicorn..."
exec uvicorn delivery.main:app --host 0.0.0.0 --port 8000 "$@"