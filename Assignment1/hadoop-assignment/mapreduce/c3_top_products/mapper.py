#!/usr/bin/env python3
import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("transaction_id,"):
            continue
        fields = line.split(",")
        if len(fields) != 9:
            continue
        product  = fields[4]
        quantity = int(fields[6])
        print(f"{product}\t{quantity}")

if __name__ == "__main__":
    main()
