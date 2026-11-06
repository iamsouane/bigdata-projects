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
        country        = fields[2]
        payment_method = fields[8]
        print(f"{country}|{payment_method}\t1")

if __name__ == "__main__":
    main()
