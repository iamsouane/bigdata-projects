#!/usr/bin/env python3
import sys

current_cat = None
count = 0
total = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    cat, c, v = line.split("\t")
    c = int(c)
    v = int(v)
    if cat == current_cat:
        count += c
        total += v
    else:
        if current_cat is not None:
            print(f"{current_cat}\t{count}\t{total}")
        current_cat = cat
        count = c
        total = v

if current_cat is not None:
    print(f"{current_cat}\t{count}\t{total}")
