#!/usr/bin/env python3
import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        product, total = line.split("\t", 1)
        total = int(total)
        # Inverser : clé = total (pour tri décroissant), valeur = produit
        # On formate sur 10 chiffres pour que le tri lexicographique = tri numérique
        print(f"{total:010d}\t{product}")

if __name__ == "__main__":
    main()
