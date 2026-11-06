#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=========================================="
echo " 1. Container status"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo " 2. HDFS DataNodes (expect: Live datanodes (3))"
echo "=========================================="
docker exec namenode hdfs dfsadmin -report | grep -E "Live datanodes|Dead datanodes|Name:|Hostname:|Configured Capacity|DFS Used%|Under replicated blocks"

echo ""
echo "=========================================="
echo " 3. YARN NodeManagers (expect: 3 RUNNING)"
echo "=========================================="
docker exec resourcemanager yarn node -list

echo ""
echo "=========================================="
echo " 4. HDFS replication factor (expect: 2)"
echo "=========================================="
docker exec namenode hdfs getconf -confKey dfs.replication

echo ""
echo "=========================================="
echo " 5. Web UIs"
echo "=========================================="
echo "NameNode : http://localhost:9870/dfshealth.html"
echo "ResourceM: http://localhost:8088/cluster/nodes"
echo ""
echo "Done."