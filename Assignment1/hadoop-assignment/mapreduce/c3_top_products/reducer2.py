#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    total, product = line.split("\t", 1)
    print(f"{product}\t{int(total)}")
