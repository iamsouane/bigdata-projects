# Hadoop 3.4.1 Distributed Cluster — Docker Compose

Cluster Hadoop 3.4.1 entièrement distribué sur Docker Compose :
- 1 NameNode, 3 DataNodes (HDFS, réplication = 2)
- 1 ResourceManager, 3 NodeManagers (YARN)
- Hadoop Streaming Python 3 pour MapReduce

## Architecture

| Service | Rôle | Ports | Volume |
|---|---|---|---|
| namenode | Maître HDFS | 9870, 8020 | namenode_data |
| datanode1 | Esclave HDFS | 9864 | datanode1_data |
| datanode2 | Esclave HDFS | 9865→9864 | datanode2_data |
| datanode3 | Esclave HDFS | 9866→9864 | datanode3_data |
| resourcemanager | Maître YARN | 8088 | — |
| nodemanager1 | Esclave YARN | — | — |
| nodemanager2 | Esclave YARN | — | — |
| nodemanager3 | Esclave YARN | — | — |

## Prérequis

- Docker Engine 24+
- Docker Compose v2
- 6 Go de RAM minimum disponibles

## Démarrage

```bash
./scripts/start.sh
```

Ou manuellement :

```bash
docker compose build
docker compose up -d
```

## Vérification

```bash
./scripts/verify.sh
```

Attendu :
- `Live datanodes (3)`
- 3 NodeManagers `RUNNING`
- `dfs.replication = 2`

Interfaces web :
- NameNode : http://localhost:9870/dfshealth.html
- ResourceManager : http://localhost:8088/cluster/nodes

## Arrêt

```bash
./scripts/stop.sh            # garde les données HDFS
docker compose down -v       # supprime aussi les volumes
```

## Configuration

Tous les fichiers XML sont dans `conf/` et montés en lecture seule
dans chaque conteneur sur `/opt/hadoop/etc/hadoop`.
Aucune configuration n'est modifiée à l'intérieur d'un conteneur :
reconstruire le cluster revient à relancer `docker compose up -d`.