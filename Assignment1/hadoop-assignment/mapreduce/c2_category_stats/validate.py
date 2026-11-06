#!/usr/bin/env python3
import csv
from collections import defaultdict

def main(csv_path="../../transactions.csv", out_path="c2_expected.tsv"):
    stats = defaultdict(lambda: [0, 0])
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            price_cents = int(round(float(row["unit_price"]) * 100))
            revenue = int(row["quantity"]) * price_cents
            cat = row["category"]
            stats[cat][0] += 1
            stats[cat][1] += revenue
    with open(out_path, "w", encoding="utf-8") as f:
        for cat in sorted(stats):
            c, t = stats[cat]
            f.write(f"{cat}\t{c}\t{t}\n")
    print(f"Écrit {out_path} avec {len(stats)} catégories.")
    for cat in sorted(stats):
        print(f"  {cat}: {stats[cat][0]} transactions, {stats[cat][1]} centimes")

if __name__ == "__main__":
    main()
