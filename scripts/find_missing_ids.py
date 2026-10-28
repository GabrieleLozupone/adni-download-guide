#!/usr/bin/env python3
"""Print the Image IDs you wanted that are missing from a collection export, a search export or an image index.

    python scripts/find_missing_ids.py wanted_ids.txt collection_export.csv > missing.txt

Both files can be a text list or a CSV (Image ID column auto-detected). A summary goes to stderr, the missing IDs to
stdout (one per line), so you can paste them back into Advanced Image Search.
"""
import argparse
import sys

from _ids import read_ids


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("wanted", help="the IDs you want (text or CSV)")
    p.add_argument("have", help="what you got: collection CSV, search CSV, image_index.csv or text")
    p.add_argument("--wanted-column")
    p.add_argument("--have-column")
    a = p.parse_args()

    wanted = read_ids(a.wanted, a.wanted_column)
    have = set(read_ids(a.have, a.have_column))
    missing = [i for i in wanted if i not in have]
    extra = len(have - set(wanted))
    print(f"wanted {len(wanted)}, found {len(wanted) - len(missing)}, missing {len(missing)}, "
          f"extra (not in wanted) {extra}", file=sys.stderr)
    for i in missing:
        print(i)


if __name__ == "__main__":
    main()
