import sys
import csv

# Lit les données reçues depuis l'entrée standard
reader = csv.reader(sys.stdin)

# Parcourt chaque ligne du fichier CSV
for row in reader:

    # Ignore les lignes qui n'ont pas 3 colonnes
    # et la ligne d'en-tête
    if len(row) != 3 or row[0] == "country":
        continue

    # Affecte les 3 colonnes à des variables
    country, product, amount = row

    try:
        # Convertit le montant en nombre décimal
        value = float(amount)

        # Affiche le pays comme clé et le montant comme valeur
        print("{}\t{}".format(country, value))

    except ValueError:
        # Ignore la ligne si le montant n'est pas numérique
        continue