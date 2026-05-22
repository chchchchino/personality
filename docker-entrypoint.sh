#!/usr/bin/env bash
set -euo pipefail

exec pm2-runtime /app/ecosystem.config.cjs
