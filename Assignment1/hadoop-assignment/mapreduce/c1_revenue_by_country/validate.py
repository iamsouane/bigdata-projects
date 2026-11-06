#!/usr/bin/env python3
import csv
from collections import defaultdict

def main(csv_path="../../transactions.csv", out_path="c1_expected.tsv"):
    totals = defaultdict(int)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            price_cents = int(round(float(row["unit_price"]) * 100))
            totals[row["country"]] += int(row["quantity"]) * price_cents

    with open(out_path, "w", encoding="utf-8") as f:
        for country in sorted(totals):
            f.write(f"{country}\t{totals[country]}\n")

    print(f"Écrit {out_path} avec {len(totals)} pays.")
    for c in sorted(totals):
        print(f"  {c}: {totals[c]} centimes")

if __name__ == "__main__":
    main()
