#!/usr/bin/env python3
"""Test the integrity of every ZIP in a folder (Zip64 supported). Exit code 1 if any ZIP fails.

    python scripts/check_zips.py /path/to/ADNI_zips
"""
import argparse
import sys
import zipfile
from pathlib import Path


def check(path):
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            n = len(z.infolist())
        return ("FAILED", f"corrupted member: {bad}") if bad else ("OK", f"{n} files")
    except (zipfile.BadZipFile, OSError, EOFError) as e:
        return "FAILED", str(e)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder")
    a = p.parse_args()

    zips = sorted(Path(a.folder).glob("*.zip"))
    if not zips:
        sys.exit(f"No .zip files in {a.folder}")
    failed = 0
    for z in zips:
        status, info = check(z)
        failed += status == "FAILED"
        print(f"{status:6}  {z.stat().st_size / 1e9:7.2f} GB  {z.name}  ({info})", flush=True)
    print(f"\n{len(zips) - failed} OK, {failed} FAILED")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
