Partie A — Construire et vérifier un cluster Hadoop 3.4.1 sur Docker

Projet : cluster Hadoop 3.4.1 entièrement distribué sur Docker Compose
Cible : Windows 10/11 avec Docker Desktop
Objectif : 1 NameNode, 3 DataNodes, 1 ResourceManager, 3 NodeManagers, réplication HDFS = 2, taille de bloc = 1 Mio.

1. Architecture

Le cluster comporte 8 conteneurs répartis sur un réseau Docker bridge hadoop-net :

Service	Rôle	Ports exposés	Volume persistant
namenode	Maître HDFS	9870 (web), 8020 (RPC)	namenode_data
datanode1	Esclave HDFS	9864 (web)	datanode1_data
datanode2	Esclave HDFS	9865 → 9864	datanode2_data
datanode3	Esclave HDFS	9866 → 9864	datanode3_data
resourcemanager	Maître YARN	8088 (web)	—
nodemanager1	Esclave YARN	—	—
nodemanager2	Esclave YARN	—	—
nodemanager3	Esclave YARN	—	—
Choix clés :

Séparation stricte DataNode / NodeManager : chaque daemon a son propre conteneur, ce qui permet d'arrêter un DataNode sans toucher au NodeManager (utile pour la partie D).
Image officielle apache/hadoop:3.4.1 : correspond exactement à la version imposée, pas de recompilation.
Plateforme linux/amd64 : indispensable sur Apple Silicon, sans effet sur Windows mais conservée pour la portabilité.
Volumes nommés : métadonnées du NameNode et blocs des DataNodes survivent aux redémarrages.
Configuration montée en lecture seule : conf/ est monté sur /opt/hadoop/etc/hadoop, garantissant une configuration identique partout.
Limite structurelle : les 8 conteneurs partagent un seul noyau et un seul disque physique. La réplication à 2 protège contre la perte d'un conteneur, pas contre une panne matérielle de l'hôte.

2. Prérequis Windows

Windows 10/11 (64 bits).
Docker Desktop installé et configuré pour utiliser le backend WSL 2 (recommandé).
WSL 2 activé (Docker Desktop le propose à l'installation).
PowerShell ou Windows Terminal (pour exécuter les commandes).
6 Go de RAM minimum alloués à Docker Desktop (Settings → Resources → Memory).
Espace disque : environ 5 Go pour les images et volumes.
Vérifie que Docker fonctionne :

powershell
docker --version
docker compose version
Tu dois voir Docker version 24+ et Docker Compose version v2+.

3. Arborescence du projet

Crée un dossier hadoop-assignment sur ton disque (par exemple C:\Users\<TonNom>\hadoop-assignment) avec cette structure :

text
hadoop-assignment/
├── Dockerfile
├── compose.yaml
├── conf/
│   ├── core-site.xml
│   ├── hdfs-site.xml
│   ├── yarn-site.xml
│   ├── mapred-site.xml
│   └── capacity-scheduler.xml
├── scripts/
│   ├── start.ps1
│   ├── stop.ps1
│   └── verify.ps1
└── README.md
Sous PowerShell :

powershell
mkdir hadoop-assignment
cd hadoop-assignment
mkdir conf, scripts
4. Dockerfile

L'image officielle apache/hadoop:3.4.1 est basée sur CentOS, pas Debian. Il faut donc utiliser yum, pas apt-get. Le Dockerfile ajoute uniquement curl, nc et procps-ng pour les healthchecks et les scripts de vérification.

dockerfile
FROM apache/hadoop:3.4.1

USER root

RUN yum install -y curl nc procps-ng \
    && yum clean all \
    && rm -rf /var/cache/yum

USER hadoop

ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin

5. Fichiers de configuration Hadoop

5.1 conf/core-site.xml

xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://namenode:8020</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/hadoop/tmp</value>
    </property>
</configuration>
5.2 conf/hdfs-site.xml

xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>2</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/hadoop/dfs/name</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/hadoop/dfs/data</value>
    </property>
    <property>
        <name>dfs.blocksize</name>
        <value>1048576</value>
    </property>
    <property>
        <name>dfs.namenode.rpc-address</name>
        <value>namenode:8020</value>
    </property>
    <property>
        <name>dfs.namenode.http-address</name>
        <value>0.0.0.0:9870</value>
    </property>
    <property>
        <name>dfs.datanode.http.address</name>
        <value>0.0.0.0:9864</value>
    </property>
    <property>
        <name>dfs.client.use.datanode.hostname</name>
        <value>true</value>
    </property>
    <property>
        <name>dfs.datanode.failed.volumes.tolerated</name>
        <value>1</value>
    </property>
</configuration>

Points importants :

dfs.blocksize = 1048576 (1 Mio) : préparation de la partie B, où l'on doit observer plusieurs blocs sur un fichier de ~7 Mo.
dfs.client.use.datanode.hostname = true : les clients résolvent les DataNodes par nom Docker.
dfs.datanode.failed.volumes.tolerated = 1 : tolère un volume défaillant, utile si un chmod échoue sous Docker Desktop.
5.3 conf/yarn-site.xml

xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>resourcemanager</value>
    </property>
    <property>
        <name>yarn.resourcemanager.webapp.address</name>
        <value>0.0.0.0:8088</value>
    </property>
    <property>
        <name>yarn.resourcemanager.address</name>
        <value>resourcemanager:8032</value>
    </property>
    <property>
        <name>yarn.resourcemanager.scheduler.address</name>
        <value>resourcemanager:8030</value>
    </property>
    <property>
        <name>yarn.resourcemanager.resource-tracker.address</name>
        <value>resourcemanager:8031</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>2048</value>
    </property>
    <property>
        <name>yarn.nodemanager.resource.cpu-vcores</name>
        <value>2</value>
    </property>
    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>512</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>2048</value>
    </property>
    <property>
        <name>yarn.scheduler.minimum-allocation-vcores</name>
        <value>1</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-vcores</name>
        <value>2</value>
    </property>
    <property>
        <name>yarn.nodemanager.pmem-check-enabled</name>
        <value>false</value>
    </property>
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME,PATH,LANG,TZ</value>
    </property>
    <property>
        <name>yarn.nodemanager.local-dirs</name>
        <value>/hadoop/yarn/local</value>
    </property>
    <property>
        <name>yarn.nodemanager.log-dirs</name>
        <value>/hadoop/yarn/log</value>
    </property>
</configuration>


Points importants :

Les adresses explicites du ResourceManager évitent les échecs de connexion aléatoires.
yarn.nodemanager.resource.cpu-vcores = 2 : sans cette propriété, le NodeManager déclare un nombre de vCores incohérent et peut être rejeté.
yarn.scheduler.minimum-allocation-mb = 512 : garantit que les 2048 Mo du NodeManager dépassent le minimum requis.
5.4 conf/mapred-site.xml

xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.env</name>
        <value>HADOOP_MAPRED_HOME=/opt/hadoop</value>
    </property>
    <property>
        <name>mapreduce.map.env</name>
        <value>HADOOP_MAPRED_HOME=/opt/hadoop</value>
    </property>
    <property>
        <name>mapreduce.reduce.env</name>
        <value>HADOOP_MAPRED_HOME=/opt/hadoop</value>
    </property>
</configuration>
5.5 conf/capacity-scheduler.xml

Le ResourceManager utilise par défaut le CapacityScheduler, qui exige une hiérarchie de queues explicite. Sans ce fichier, il échoue avec Queue configuration missing child queue names for root.

xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>yarn.scheduler.capacity.root.queues</name>
        <value>default</value>
    </property>
    <property>
        <name>yarn.scheduler.capacity.root.default.capacity</name>
        <value>100</value>
    </property>
    <property>
        <name>yarn.scheduler.capacity.root.default.maximum-capacity</name>
        <value>100</value>
    </property>
    <property>
        <name>yarn.scheduler.capacity.root.default.state</name>
        <value>RUNNING</value>
    </property>
    <property>
        <name>yarn.scheduler.capacity.root.default.user-limit-factor</name>
        <value>1</value>
    </property>
</configuration>
6. compose.yaml

yaml
services:

  namenode:
    build: .
    platform: linux/amd64
    container_name: namenode
    hostname: namenode
    networks:
      - hadoop-net
    ports:
      - "9870:9870"
      - "8020:8020"
    volumes:
      - namenode_data:/hadoop/dfs/name
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/dfs/name;
      chown -R hadoop:hadoop /hadoop/dfs/name;
      if [ ! -d /hadoop/dfs/name/current ]; then
        echo 'Formatting NameNode...';
        su hadoop -c 'hdfs namenode -format -force -nonInteractive';
      fi;
      exec su hadoop -c 'hdfs namenode'
      "
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:9870/dfshealth.html >/dev/null || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 15
      start_period: 30s

  datanode1:
    build: .
    platform: linux/amd64
    container_name: datanode1
    hostname: datanode1
    networks:
      - hadoop-net
    ports:
      - "9864:9864"
    volumes:
      - datanode1_data:/hadoop/dfs/data
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/dfs/data;
      chown -R hadoop:hadoop /hadoop/dfs/data;
      exec su hadoop -c 'hdfs datanode'
      "
    depends_on:
      namenode:
        condition: service_healthy

  datanode2:
    build: .
    platform: linux/amd64
    container_name: datanode2
    hostname: datanode2
    networks:
      - hadoop-net
    ports:
      - "9865:9864"
    volumes:
      - datanode2_data:/hadoop/dfs/data
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/dfs/data;
      chown -R hadoop:hadoop /hadoop/dfs/data;
      exec su hadoop -c 'hdfs datanode'
      "
    depends_on:
      namenode:
        condition: service_healthy

  datanode3:
    build: .
    platform: linux/amd64
    container_name: datanode3
    hostname: datanode3
    networks:
      - hadoop-net
    ports:
      - "9866:9864"
    volumes:
      - datanode3_data:/hadoop/dfs/data
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/dfs/data;
      chown -R hadoop:hadoop /hadoop/dfs/data;
      exec su hadoop -c 'hdfs datanode'
      "
    depends_on:
      namenode:
        condition: service_healthy

  resourcemanager:
    build: .
    platform: linux/amd64
    container_name: resourcemanager
    hostname: resourcemanager
    networks:
      - hadoop-net
    ports:
      - "8088:8088"
    volumes:
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      exec su hadoop -c 'yarn resourcemanager'
      "
    depends_on:
      namenode:
        condition: service_healthy

  nodemanager1:
    build: .
    platform: linux/amd64
    container_name: nodemanager1
    hostname: nodemanager1
    networks:
      - hadoop-net
    volumes:
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/yarn/local /hadoop/yarn/log;
      chown -R hadoop:hadoop /hadoop/yarn;
      exec su hadoop -c 'yarn nodemanager'
      "
    depends_on:
      resourcemanager:
        condition: service_started

  nodemanager2:
    build: .
    platform: linux/amd64
    container_name: nodemanager2
    hostname: nodemanager2
    networks:
      - hadoop-net
    volumes:
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/yarn/local /hadoop/yarn/log;
      chown -R hadoop:hadoop /hadoop/yarn;
      exec su hadoop -c 'yarn nodemanager'
      "
    depends_on:
      resourcemanager:
        condition: service_started

  nodemanager3:
    build: .
    platform: linux/amd64
    container_name: nodemanager3
    hostname: nodemanager3
    networks:
      - hadoop-net
    volumes:
      - ./conf:/opt/hadoop/etc/hadoop:ro
    user: root
    command: >
      bash -c "
      mkdir -p /hadoop/yarn/local /hadoop/yarn/log;
      chown -R hadoop:hadoop /hadoop/yarn;
      exec su hadoop -c 'yarn nodemanager'
      "
    depends_on:
      resourcemanager:
        condition: service_started

volumes:
  namenode_data:
  datanode1_data:
  datanode2_data:
  datanode3_data:

networks:
  hadoop-net:
    driver: bridge
Points importants du compose.yaml :

Chaque daemon tourne via user: root puis su hadoop : Hadoop refuse de tourner en root, mais les volumes Docker doivent être préparés en root pour éviter les erreurs EPERM sur chmod.
Le NameNode se formate automatiquement au premier démarrage si /hadoop/dfs/name/current n'existe pas.
Les DataNodes et le ResourceManager attendent que le NameNode soit sain (depends_on + healthcheck).
Les NodeManagers attendent le ResourceManager.
7. Scripts PowerShell

Sous Windows, les scripts shell .sh ne s'exécutent pas directement. Voici les équivalents PowerShell.

7.1 scripts/start.ps1

powershell
# Démarre le cluster Hadoop
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> Building images..."
docker compose build

Write-Host "==> Starting cluster..."
docker compose up -d

Write-Host "==> Waiting for NameNode to become healthy..."
$healthy = $false
for ($i = 0; $i -lt 60; $i++) {
    $result = docker exec namenode curl -fsS http://localhost:9870/dfshealth.html 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "NameNode is healthy."
        $healthy = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $healthy) {
    Write-Host "NameNode did not become healthy in time. Check logs: docker logs namenode"
    exit 1
}

Write-Host "==> Waiting for 3 DataNodes to register..."
for ($i = 0; $i -lt 60; $i++) {
    $report = docker exec -u hadoop namenode hdfs dfsadmin -report 2>$null
    if ($report -match "Live datanodes \(3\)") {
        Write-Host "3 DataNodes registered."
        break
    }
    Start-Sleep -Seconds 2
}

Write-Host "==> Cluster started. Run scripts\verify.ps1 to confirm."
7.2 scripts/stop.ps1

powershell
# Arrête le cluster (les volumes sont préservés)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> Stopping cluster (volumes preserved)..."
docker compose down

Write-Host "==> To also delete HDFS data, run: docker compose down -v"
7.3 scripts/verify.ps1

powershell
# Vérifie l'état du cluster
$ErrorActionPreference = "Continue"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "=========================================="
Write-Host " 1. Container status"
Write-Host "=========================================="
docker compose ps

Write-Host ""
Write-Host "=========================================="
Write-Host " 2. HDFS DataNodes (expect: Live datanodes (3))"
Write-Host "=========================================="
docker exec -u hadoop namenode hdfs dfsadmin -report | Select-String -Pattern "Live datanodes|Hostname:|Configured Capacity|DFS Used%|Under replicated blocks"

Write-Host ""
Write-Host "=========================================="
Write-Host " 3. YARN NodeManagers (expect: 3 RUNNING)"
Write-Host "=========================================="
docker exec -u hadoop resourcemanager yarn node -list

Write-Host ""
Write-Host "=========================================="
Write-Host " 4. HDFS replication factor (expect: 2)"
Write-Host "=========================================="
docker exec -u hadoop namenode hdfs getconf -confKey dfs.replication

Write-Host ""
Write-Host "=========================================="
Write-Host " 5. Web UIs"
Write-Host "=========================================="
Write-Host "NameNode : http://localhost:9870/dfshealth.html"
Write-Host "ResourceM: http://localhost:8088/cluster/nodes"
Write-Host ""
Write-Host "Done."
Note PowerShell : par défaut, PowerShell peut bloquer l'exécution des scripts. Si tu vois une erreur du type « l'exécution de scripts est désactivée sur ce système », exécute une fois :

powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
8. README.md

markdown
# Hadoop 3.4.1 Distributed Cluster — Docker Compose

Cluster Hadoop 3.4.1 entièrement distribué :
- 1 NameNode, 3 DataNodes (HDFS, réplication = 2)
- 1 ResourceManager, 3 NodeManagers (YARN)
- Hadoop Streaming Python 3 pour MapReduce

## Prérequis Windows

- Windows 10/11, Docker Desktop avec backend WSL 2
- 6 Go de RAM alloués à Docker Desktop
- PowerShell

## Démarrage

```powershell
cd hadoop-assignment
.\scripts\start.ps1
```

Ou manuellement :

```powershell
docker compose build
docker compose up -d
```

## Vérification

```powershell
.\scripts\verify.ps1
```

Attendu :
- `Live datanodes (3)`
- 3 NodeManagers `RUNNING`
- `dfs.replication = 2`

Interfaces web :
- NameNode : http://localhost:9870/dfshealth.html
- ResourceManager : http://localhost:8088/cluster/nodes

## Arrêt

```powershell
.\scripts\stop.ps1            # garde les données HDFS
docker compose down -v        # supprime aussi les volumes
```

## Configuration

Tous les fichiers XML sont dans `conf/` et montés en lecture seule
dans chaque conteneur sur `/opt/hadoop/etc/hadoop`.
Aucune configuration n'est modifiée dans un conteneur :
reconstruire le cluster revient à relancer `docker compose up -d`.
9. Procédure complète sous Windows

Étape 1 — Créer l'arborescence

powershell
cd C:\Users\<TonNom>
mkdir hadoop-assignment
cd hadoop-assignment
mkdir conf, scripts
Étape 2 — Créer les fichiers

Crée chaque fichier avec les contenus des sections 4 à 8 :

Dockerfile
compose.yaml
conf/core-site.xml
conf/hdfs-site.xml
conf/yarn-site.xml
conf/mapred-site.xml
conf/capacity-scheduler.xml
scripts/start.ps1
scripts/stop.ps1
scripts/verify.ps1
README.md
Attention : sous Windows, les fichiers XML doivent être enregistrés en UTF-8 sans BOM. Dans Notepad, choisis « UTF-8 » à l'enregistrement. Dans VS Code, l'encodage par défaut est UTF-8 sans BOM.

Étape 3 — Démarrer le cluster

powershell
.\scripts\start.ps1
Le premier démarrage télécharge l'image apache/hadoop:3.4.1 (~1 Go) et construit 8 images dérivées. Cela peut prendre 5 à 15 minutes selon la connexion.

Étape 4 — Vérifier

powershell
.\scripts\verify.ps1
Étape 5 — Captures d'écran

docker exec -u hadoop namenode hdfs dfsadmin -report → Live datanodes (3).
docker exec -u hadoop resourcemanager yarn node -list → Total Nodes:3, 3 RUNNING.
Navigateur : http://localhost:9870/dfshealth.html → 3 DataNodes vivants.
Navigateur : http://localhost:8088/cluster/nodes → 3 NodeManagers.
10. Difficultés rencontrées et solutions

Ces difficultés ont été rencontrées et résolues pendant la construction du cluster. Elles sont valorisées dans la notation.

Difficulté	Cause	Solution
apt-get: command not found	L'image apache/hadoop:3.4.1 est basée sur CentOS, pas Debian	Remplacer apt-get par yum
Directory /hadoop/dfs/name is in an inconsistent state	Répertoire du NameNode absent ou permissions incorrectes	mkdir -p + chown avant formatage
EPERM sur chmod côté DataNodes	Permissions du volume Docker	user: root + chown + su hadoop ; ajout de dfs.datanode.failed.volumes.tolerated = 1
Queue configuration missing child queue names for root	Fichier capacity-scheduler.xml manquant	Ajout du fichier avec la queue default
Total Nodes:0 côté YARN	vCores non déclarés, minimum d'allocation incohérent, adresses RM implicites	Ajout de yarn.nodemanager.resource.cpu-vcores, yarn.scheduler.minimum-allocation-vcores, adresses RM explicites
11. Ce que la partie A prouve

Le cluster est opérationnel : 8 conteneurs Up.
Les 3 DataNodes sont enregistrés (Live datanodes (3)).
Les 3 NodeManagers sont RUNNING (Total Nodes:3).
La réplication HDFS est bien à 2.
La taille de bloc est à 1 Mio (préparation de la partie B).
Les interfaces web NameNode (9870) et ResourceManager (8088) répondent.
Ce qui n'est pas encore prouvé : le stockage effectif de données dans HDFS, l'exécution de MapReduce sur YARN, la tolérance aux pannes. Ce sera l'objet des parties B, C et D.

12. Limites

Un seul noyau, un seul disque : les 8 conteneurs partagent l'infrastructure de la machine hôte. La réplication à 2 protège contre la perte d'un conteneur DataNode, mais pas contre une panne du disque physique.
Ressources limitées : chaque NodeManager dispose de 2 Go de mémoire et 2 vCores, ce qui suffit pour les traitements MapReduce du devoir mais limite l'exécution de jobs lourds simultanés.
Aucune haute disponibilité : le NameNode est un point unique de défaillance (un Standby NameNode serait nécessaire pour la HA, hors périmètre du devoir).
Fin du document de la partie A. La partie B (import de transactions.csv dans HDFS, vérification de la distribution en blocs via hdfs fsck) peut être traitée dans un document séparé.