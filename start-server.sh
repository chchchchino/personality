#!/usr/bin/env bash
set -euo pipefail

cd /app/server
exec /opt/uv-venv/bin/uv run personality-server
