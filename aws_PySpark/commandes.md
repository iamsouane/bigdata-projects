# Commandes du devoir — bucket `tp-emr-souane-2026`

> Remplacer `PUBLIC_DNS_PRIMARY` par le DNS public du Primary Node (page du cluster EMR)
> et `application_XXXXXXXXXXXX_XXXX` par l'ID réel affiché par `yarn application -list`.

## Partie 6 — Connexion SSH et vérifications

Depuis votre Mac (dans le dossier contenant la clé) :

```bash
chmod 400 emr-tp-key.pem
ssh -i emr-tp-key.pem hadoop@PUBLIC_DNS_PRIMARY
```

Une fois connecté sur le Primary Node :

```bash
hostname
python3 --version
spark-submit --version
yarn node -list
yarn node -list -all
```

## Partie 8 — Soumettre le traitement Spark

### Méthode A — SSH et spark-submit (sur le Primary Node)

```bash
aws s3 cp s3://tp-emr-souane-2026/Application/spark.py /home/hadoop/spark.py

spark-submit --master yarn --deploy-mode cluster /home/hadoop/spark.py \
  s3://tp-emr-souane-2026/Input/transaction.csv \
  s3://tp-emr-souane-2026/Output/revenue_by_country/
```

Suivi et logs (en mode cluster, `show()` apparaît dans les logs YARN) :

```bash
yarn application -list -appStates ALL
yarn logs -applicationId application_XXXXXXXXXXXX_XXXX
```

Astuce : `yarn logs -applicationId application_XXXXXXXXXXXX_XXXX | grep -A 12 "TotalRevenue"` pour retrouver le tableau.

### Méthode B — EMR Step (console)

| Champ | Valeur |
|---|---|
| Type | Spark application |
| Nom | `RevenueByCountry` |
| Deploy mode | Cluster |
| Application location | `s3://tp-emr-souane-2026/Application/spark.py` |
| Arguments | `s3://tp-emr-souane-2026/Input/transaction.csv s3://tp-emr-souane-2026/Output/revenue_by_country/` |

## Partie 9 — Vérification des résultats Parquet

```bash
aws s3 ls s3://tp-emr-souane-2026/Output/revenue_by_country/ --recursive
```

Attendu : un fichier `part-*.parquet` et un marqueur `_SUCCESS`.

Récupérer `verify.py` sur le Primary Node (après l'avoir déposé dans `Application/`) puis lancer :

```bash
aws s3 cp s3://tp-emr-souane-2026/Application/verify.py /home/hadoop/verify.py
spark-submit --master yarn --deploy-mode client /home/hadoop/verify.py
```

(Alternative sans S3 : `nano verify.py` sur le Primary Node et coller le contenu.)

Comparer la sortie avec `reference_revenue_by_country.csv` (calcul pandas local).

## Rappel — Partie 10

Terminer le cluster dans la console EMR juste après validation, vérifier que les 3 instances EC2 sont `terminated`, puis supprimer la règle SSH temporaire.
