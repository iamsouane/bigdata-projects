#!/usr/bin/env python3
import sys

current_product = None
current_total   = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    product, qty = line.split("\t", 1)
    qty = int(qty)
    if product == current_product:
        current_total += qty
    else:
        if current_product is not None:
            print(f"{current_product}\t{current_total}")
        current_product = product
        current_total   = qty

if current_product is not None:
    print(f"{current_product}\t{current_total}")
