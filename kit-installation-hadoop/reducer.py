import sys

# Pays actuellement en cours de traitement
current_country = None

# Total cumulé pour ce pays
total = 0.0

# Lire les données reçues depuis l'entrée standard
for line in sys.stdin:
    line = line.strip()

    try:
        # Séparer le pays et le montant à partir de la tabulation
        country, amount = line.split("\t", 1)
        amount = float(amount)
    except ValueError:
        # Ignorer les lignes incorrectes
        continue

    # Si la ligne appartient au même pays, ajouter le montant
    if current_country == country:
        total += amount

    else:
        # Afficher le total du pays précédent
        if current_country is not None:
            print("{}\t{}".format(current_country, total))

        # Commencer le calcul pour le nouveau pays
        current_country = country
        total = amount

# Afficher le total du dernier pays
if current_country is not None:
    print("{}\t{}".format(current_country, total))