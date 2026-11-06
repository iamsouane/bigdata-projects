#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Building images..."
docker compose build

echo "==> Starting cluster..."
docker compose up -d

echo "==> Waiting for NameNode to become healthy..."
for i in $(seq 1 60); do
    if docker exec namenode curl -fsS http://localhost:9870/dfshealth.html >/dev/null 2>&1; then
        echo "NameNode is healthy."
        break
    fi
    sleep 2
done

echo "==> Waiting for 3 DataNodes to register..."
for i in $(seq 1 60); do
    live=$(docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep -c "Live datanodes" || true)
    count=$(docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep -oP 'Live datanodes \(\K[0-9]+' || echo 0)
    if [ "$count" = "3" ]; then
        echo "3 DataNodes registered."
        break
    fi
    sleep 2
done

echo "==> Cluster started. Run scripts/verify.sh to confirm."