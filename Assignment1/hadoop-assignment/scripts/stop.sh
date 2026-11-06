#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Stopping cluster (volumes preserved)..."
docker compose down

echo "==> To also delete HDFS data, run: docker compose down -v"