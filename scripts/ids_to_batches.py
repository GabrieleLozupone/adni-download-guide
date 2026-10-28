#!/usr/bin/env python3
"""Split a list of Image IDs into comma-separated batches to paste into IDA's Advanced Image Search.

Input: a text file (IDs separated by newlines, commas or spaces; 'I123' and '123' both work) or a CSV with an
Image ID column (auto-detected, or --column).

    python scripts/ids_to_batches.py wanted_ids.txt --size 500 --out batches.txt
"""
import argparse

from _ids import read_ids


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="text file or CSV with Image IDs")
    p.add_argument("--column", help="CSV column with the Image IDs (default: auto-detect)")
    p.add_argument("--size", type=int, default=500, help="IDs per batch (default 500)")
    p.add_argument("--out", help="write batches here, one per line (default: print)")
    a = p.parse_args()

    ids = read_ids(a.input, a.column)
    batches = [ids[i:i + a.size] for i in range(0, len(ids), a.size)]
    lines = [",".join(b) for b in batches]
    if a.out:
        with open(a.out, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"{len(ids)} unique IDs -> {len(batches)} batches of up to {a.size} in {a.out}")
    else:
        for n, line in enumerate(lines, 1):
            print(f"# batch {n} ({len(batches[n - 1])} IDs)")
            print(line)


if __name__ == "__main__":
    main()
