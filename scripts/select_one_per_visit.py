#!/usr/bin/env python3
"""Keep one image per subject x date x modality from an IDA Advanced Search CSV export.

You decide the preference with --prefer: regular expressions matched (case-insensitive) against the Description
column, best first. Among images of the same group, the one matching the earliest pattern wins; ties go to the lowest
Image ID, so the result is reproducible. Images matching no pattern are used only when nothing better exists (or never,
with --strict).

    python scripts/select_one_per_visit.py search_results.csv \\
        --prefer "GradWarp.*N3" "Accelerated Sagittal MPRAGE" "MPRAGE" --out selected.csv

PET: modality is just "PET" for every tracer, so run it once per tracer (search one tracer at a time), or add a
column that separates them with --group-by.
"""
import argparse
import csv
import re
import sys
from collections import defaultdict

from _ids import find_id_column, normalize_id, read_csv_rows


def pick(fieldnames, wanted, default):
    for name in wanted:
        if name in fieldnames:
            return name
    return default


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv", help="CSV downloaded from IDA Advanced Image Search results")
    p.add_argument("--prefer", nargs="+", required=True, help="regexes on Description, best first")
    p.add_argument("--strict", action="store_true", help="drop images that match no --prefer pattern")
    p.add_argument("--group-by", nargs="*", default=[], help="extra columns that define a group")
    p.add_argument("--out", required=True, help="output CSV with the chosen rows")
    p.add_argument("--ids-out", help="also write the chosen Image IDs, one per line")
    a = p.parse_args()

    fieldnames, rows = read_csv_rows(a.csv)
    id_col = find_id_column(fieldnames)
    subj = pick(fieldnames, ["Subject ID", "Subject"], None)
    date = pick(fieldnames, ["Study Date", "Acq Date", "Scan Date"], None)
    modality = pick(fieldnames, ["Modality"], None)
    desc = pick(fieldnames, ["Description", "Series Description"], None)
    for name, col in [("subject", subj), ("date", date), ("description", desc)]:
        if col is None:
            sys.exit(f"No {name} column found. Add it under 'Display in result' in Advanced Search.")
    for col in a.group_by:
        if col not in fieldnames:
            sys.exit(f"--group-by column '{col}' not in CSV")
    patterns = [re.compile(x, re.IGNORECASE) for x in a.prefer]

    def rank(row):
        for i, pat in enumerate(patterns):
            if pat.search(row.get(desc, "")):
                return i
        return len(patterns)

    groups = defaultdict(list)
    for r in rows:
        key = (r[subj], r[date], r.get(modality, "") if modality else "") + tuple(r[c] for c in a.group_by)
        groups[key].append(r)

    chosen, ties, unmatched_groups = [], 0, 0
    for key in sorted(groups):
        cands = sorted(groups[key], key=lambda r: (rank(r), int(normalize_id(r[id_col]) or 0)))
        best = cands[0]
        if rank(best) == len(patterns):
            unmatched_groups += 1
            if a.strict:
                continue
        if len(cands) > 1 and rank(cands[1]) == rank(best):
            ties += 1
        chosen.append(best)

    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(chosen)
    if a.ids_out:
        with open(a.ids_out, "w") as f:
            f.write("\n".join(normalize_id(r[id_col]) for r in chosen) + "\n")

    print(f"{len(rows)} images in {len(groups)} subject/date/modality groups -> {len(chosen)} chosen")
    print(f"groups where the winner matched no --prefer pattern: {unmatched_groups}"
          + (" (dropped, --strict)" if a.strict else " (kept; review them)"))
    print(f"groups with a tie at the same preference level (lowest Image ID kept): {ties}")


if __name__ == "__main__":
    main()
