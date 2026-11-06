#!/usr/bin/env python3
import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line.startswith("transaction_id,"):
            continue
        fields = line.split(",")
        if len(fields) != 9:
            continue
        country    = fields[2]
        quantity   = int(fields[6])
        unit_price = fields[7]
        price_cents   = int(round(float(unit_price) * 100))
        revenue_cents = quantity * price_cents
        print(f"{country}\t{revenue_cents}")

if __name__ == "__main__":
    main()
