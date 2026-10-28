"""Shared helpers: read Image IDs from a text file or a CSV exported from IDA or ADNI tables."""
import csv
import re
import sys

# Column names that hold an IDA Image ID, in order of preference.
KNOWN_ID_COLUMNS = [
    "Image ID", "Image Data ID", "image_id", "IMAGEUID", "LONIImage",
    "PHC_LONIUID", "LONI_IMAGE", "ImageID",
]


def normalize_id(value):
    """'I000123', 'D000123', ' 123 ', '123.0' -> '123'. Returns None if no number."""
    s = str(value).strip()
    if re.fullmatch(r"\d+\.0", s):  # numbers saved as floats by spreadsheets
        s = s[:-2]
    m = re.search(r"\d+", s)
    return m.group(0) if m else None


def find_id_column(fieldnames, column=None):
    if column:
        if column not in fieldnames:
            sys.exit(f"Column '{column}' not found. Available: {', '.join(fieldnames)}")
        return column
    for name in KNOWN_ID_COLUMNS:
        if name in fieldnames:
            return name
    for name in fieldnames:
        low = name.lower().replace("_", " ")
        if "image" in low and "id" in low:
            return name
    sys.exit("Could not find an Image ID column; pass --column. Available: " + ", ".join(fieldnames))


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def read_ids(path, column=None):
    """Return Image IDs (as strings, order kept, duplicates removed) from a .csv or a plain text file."""
    if path.lower().endswith(".csv"):
        fieldnames, rows = read_csv_rows(path)
        col = find_id_column(fieldnames, column)
        raw = [r.get(col, "") for r in rows]
    else:
        with open(path, encoding="utf-8") as f:
            raw = re.split(r"[\s,;]+", f.read())
    ids, seen = [], set()
    for value in raw:
        i = normalize_id(value) if value else None
        if i and i not in seen:
            seen.add(i)
            ids.append(i)
    return ids
