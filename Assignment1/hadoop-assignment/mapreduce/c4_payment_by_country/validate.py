#!/usr/bin/env python3
import csv
from collections import defaultdict

def main(csv_path="../../transactions.csv", out_path="c4_expected.tsv"):
    counts = defaultdict(int)
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = f"{row['country']}|{row['payment_method']}"
            counts[key] += 1
    ordered = sorted(counts.items())
    with open(out_path, "w", encoding="utf-8") as f:
        for key, c in ordered:
            f.write(f"{key}\t{c}\n")
    print(f"Écrit {out_path} avec {len(ordered)} couples (pays|paiement).")
    for key, c in ordered:
        print(f"  {key}: {c}")

if __name__ == "__main__":
    main()
