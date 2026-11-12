# -*- coding: utf-8 -*-
"""
verify.py : relecture et contrôle du résultat Parquet produit par spark.py

Lancement sur le Primary Node :
    spark-submit --master yarn --deploy-mode client verify.py

Un chemin différent peut être passé en argument (ex. test local) :
    spark-submit verify.py ./output_local/
"""

import sys

from pyspark.sql import SparkSession, functions as F

# Création de la SparkSession dédiée à la vérification
spark = SparkSession.builder.appName("VerifyRevenueResults").getOrCreate()

# Chemin du répertoire Parquet (par défaut : la sortie S3 du devoir)
path = (sys.argv[1] if len(sys.argv) > 1
        else "s3://tp-emr-souane-2026/Output/revenue_by_country/")

# Lecture du répertoire Parquet : Spark lit tous les fichiers part-*.parquet.
# Le schéma est stocké dans Parquet, pas besoin d'inferSchema.
df = spark.read.parquet(path)
df.printSchema()  # attendu : Country (string), TotalRevenue (double)

# L'ordre des lignes n'est pas garanti à la relecture : on retrie donc
# explicitement (revenu décroissant, puis pays croissant).
df.orderBy(F.desc("TotalRevenue"), F.asc("Country")).show(100, truncate=False)

# Nombre de pays (chaque pays doit apparaître une seule fois)
print("Nombre de pays :", df.count())

spark.stop()
