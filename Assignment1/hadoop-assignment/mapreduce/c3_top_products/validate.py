#!/usr/bin/env python3
import csv
from collections import defaultdict

def main(csv_path="../../transactions.csv", out_path="c3_expected.tsv"):
    totals = defaultdict(int)
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            totals[row["product"]] += int(row["quantity"])
    # Tri par quantité décroissante, puis par nom pour stabilité
    ordered = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    with open(out_path, "w", encoding="utf-8") as f:
        for product, qty in ordered:
            f.write(f"{product}\t{qty}\n")
    print(f"Écrit {out_path} avec {len(ordered)} produits.")
    for product, qty in ordered:
        print(f"  {product}: {qty}")

if __name__ == "__main__":
    main()
