#!/usr/bin/env python3
"""
C1 - Reducer : somme des CA par pays.
Entrée  : country \t revenue_cents
Sortie  : country \t total_revenue_cents
"""
import sys

current_country = None
current_total   = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    country, value = line.split("\t", 1)
    value = int(value)

    if country == current_country:
        current_total += value
    else:
        if current_country is not None:
            print(f"{current_country}\t{current_total}")
        current_country = country
        current_total   = value

# Dernier pays
if current_country is not None:
    print(f"{current_country}\t{current_total}")