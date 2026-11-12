# -*- coding: utf-8 -*-
"""
spark.py : chiffre d'affaires total par pays (Amazon EMR / PySpark)

Entrée  : fichier CSV des transactions (ex. s3://tp-emr-souane-2026/Input/transaction.csv)
Sortie  : répertoire Parquet         (ex. s3://tp-emr-souane-2026/Output/revenue_by_country/)

Schéma réel du fichier transaction.csv :
    transaction_id, date, country, city, product, category,
    quantity, unit_price, payment_method
Il n'y a PAS de colonne de montant : le revenu est donc calculé
avec la formule Revenue = quantity × unit_price.

Usage :
    spark-submit spark.py <input_path> <output_path>
"""

import sys

from pyspark.sql import SparkSession, functions as F


def main(input_path, output_path):
    # ------------------------------------------------------------------
    # 1. Création de la SparkSession
    # La SparkSession est le point d'entrée de toute application Spark :
    # elle permet de lire des données, de créer des DataFrames et de
    # lancer des traitements. Sur EMR, elle se connecte automatiquement
    # à YARN, qui alloue les executors sur les nœuds Core.
    # ------------------------------------------------------------------
    spark = SparkSession.builder.appName("RevenueByCountry").getOrCreate()

    try:
        # --------------------------------------------------------------
        # 2. Lecture du fichier CSV
        # - header=true      : la première ligne contient les noms de colonnes
        # - inferSchema=true : Spark parcourt les données pour deviner les
        #   types (int, double, string...) au lieu de tout lire en texte.
        # Spark lit le fichier en partitions, traitées en parallèle par
        # les executors.
        # --------------------------------------------------------------
        df = (spark.read.option("header", "true")
              .option("inferSchema", "true")
              .csv(input_path))
        df.printSchema()  # affiche les colonnes et leurs types détectés

        # --------------------------------------------------------------
        # 3. Noms des colonnes adaptés au schéma réel du fichier
        # (l'énoncé suppose Country / Quantity / UnitPrice ; le fichier
        # réel utilise country / quantity / unit_price, en minuscules).
        # --------------------------------------------------------------
        country_col = "country"
        quantity_col = "quantity"
        price_col = "unit_price"

        # --------------------------------------------------------------
        # 4. Vérification de la présence des colonnes nécessaires
        # On échoue immédiatement avec un message clair plutôt que de
        # laisser Spark lever une erreur moins lisible plus tard.
        # --------------------------------------------------------------
        required = {country_col, quantity_col, price_col}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"Colonnes absentes : {missing}; disponibles : {df.columns}")

        # --------------------------------------------------------------
        # 5. Nettoyage des données
        # - trim      : supprime les espaces parasites autour du pays
        # - cast      : force les types numériques (double) ; une valeur
        #               non numérique devient null
        # - alias     : renomme en Country / Quantity / UnitPrice pour que
        #               la sortie respecte les noms attendus par l'énoncé
        # - dropna    : élimine les lignes ayant une valeur manquante
        # - filtres   : pays non vide, quantité strictement positive,
        #               prix unitaire positif ou nul
        # --------------------------------------------------------------
        clean = (df.select(
                    F.trim(F.col(country_col)).alias("Country"),
                    F.col(quantity_col).cast("double").alias("Quantity"),
                    F.col(price_col).cast("double").alias("UnitPrice"))
                 .dropna(subset=["Country", "Quantity", "UnitPrice"])
                 .filter(F.col("Country") != "")
                 .filter(F.col("Quantity") > 0)
                 .filter(F.col("UnitPrice") >= 0))

        # --------------------------------------------------------------
        # 6. Calcul du chiffre d'affaires par pays
        # - withColumn : Revenue = Quantity × UnitPrice (par transaction)
        # - groupBy    : regroupe les transactions d'un même pays
        #                (provoque un "shuffle" entre executors)
        # - agg(sum)   : additionne les revenus de chaque pays, arrondi
        #                à 2 décimales
        # - orderBy    : tri par revenu décroissant, puis par nom de pays
        #                croissant en cas d'égalité (ordre déterministe)
        # --------------------------------------------------------------
        result = (clean.withColumn("Revenue",
                                   F.col("Quantity") * F.col("UnitPrice"))
                  .groupBy("Country")
                  .agg(F.round(F.sum("Revenue"), 2).alias("TotalRevenue"))
                  .orderBy(F.desc("TotalRevenue"), F.asc("Country")))

        # Affichage du classement (dans les logs YARN en mode cluster)
        result.show(100, truncate=False)

        # --------------------------------------------------------------
        # 7. Écriture du résultat au format Parquet
        # - coalesce(1)       : regroupe le résultat en une seule partition
        #                       => un seul fichier part-*.parquet (adapté à
        #                       ce petit résultat, déconseillé à grande échelle)
        # - mode("overwrite") : remplace la sortie si elle existe déjà
        # Spark écrit un RÉPERTOIRE contenant part-*.parquet et _SUCCESS.
        # --------------------------------------------------------------
        (result.coalesce(1)
         .write.mode("overwrite")
         .parquet(output_path))
        print("Sortie Parquet :", output_path)

    finally:
        # --------------------------------------------------------------
        # 8. Arrêt de la SparkSession, même en cas d'erreur
        # Libère les ressources (executors / containers YARN).
        # --------------------------------------------------------------
        spark.stop()


# ----------------------------------------------------------------------
# Point d'entrée : les chemins d'entrée et de sortie sont passés en
# arguments par spark-submit (sys.argv[1] et sys.argv[2]), ce qui permet
# d'utiliser le même script en local et sur S3 sans le modifier.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: spark-submit spark.py <input_s3> <output_s3>")
    main(sys.argv[1], sys.argv[2])
