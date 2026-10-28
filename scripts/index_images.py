#!/usr/bin/env python3
"""Index unpacked IDA images into a CSV, one row per image.

IDA ZIPs unpack to  ADNI/<Subject ID>/<Description>/<YYYY-MM-DD_hh_mm_ss.f>/I<Image ID>/<files>
and contain no metadata table, so this reads everything from the folder path.

    python scripts/index_images.py /path/to/ADNI_raw/ADNI --out image_index.csv
"""
import argparse
import csv
import os
import re
import sys
from collections import Counter

IMAGE_DIR = re.compile(r"^[ID](\d+)$")
FIELDS = ["subject_id", "description", "acq_date", "acq_time", "image_id", "n_files", "format", "path"]


def file_format(names):
    exts = Counter()
    for n in names:
        low = n.lower()
        if low.endswith((".nii", ".nii.gz")):
            exts["nifti"] += 1
        elif low.endswith(".dcm"):
            exts["dicom"] += 1
        else:
            exts["other"] += 1
    return "+".join(sorted(exts)) if exts else "empty"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", help="the unpacked 'ADNI' folder")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    rows = []
    for dirpath, dirnames, filenames in os.walk(a.root):
        m = IMAGE_DIR.match(os.path.basename(dirpath))
        if not m:
            continue
        rel = os.path.relpath(dirpath, a.root).split(os.sep)
        if len(rel) < 4:
            print(f"skipping unexpected layout: {dirpath}", file=sys.stderr)
            continue
        subject, description, stamp = rel[-4], rel[-3], rel[-2]
        date, _, time = stamp.partition("_")
        rows.append({
            "subject_id": subject, "description": description, "acq_date": date,
            "acq_time": time.replace("_", ":"), "image_id": m.group(1), "n_files": len(filenames),
            "format": file_format(filenames), "path": dirpath,
        })

    rows.sort(key=lambda r: (r["subject_id"], r["acq_date"], r["image_id"]))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    dup = [i for i, c in Counter(r["image_id"] for r in rows).items() if c > 1]
    print(f"{len(rows)} images, {len({r['subject_id'] for r in rows})} subjects -> {a.out}")
    print("formats: " + ", ".join(f"{k} {v}" for k, v in Counter(r["format"] for r in rows).most_common()))
    if dup:
        print(f"warning: {len(dup)} Image IDs appear in more than one folder", file=sys.stderr)


if __name__ == "__main__":
    main()
