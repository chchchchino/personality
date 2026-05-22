#!/usr/bin/env bash
set -euo pipefail

SERVER_HOST="${SERVER_HOST:-127.0.0.1}"
SERVER_PORT="${SERVER_PORT:-8000}"
CLIENT_HOST="${CLIENT_HOST:-0.0.0.0}"
CLIENT_PORT="${CLIENT_PORT:-4200}"

cleanup() {
  if [[ -n "${server_pid:-}" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd /app/server
uv run uvicorn personality_server.app:app --host "$SERVER_HOST" --port "$SERVER_PORT" &
server_pid=$!

cd /app/client
exec npm start -- --host "$CLIENT_HOST" --port "$CLIENT_PORT" --proxy-config proxy.conf.json
