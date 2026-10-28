"""Tests on synthetic, made-up data only (no ADNI data)."""
import csv
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, check=False)


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


class TestScripts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_batches_and_normalization(self):
        (self.tmp / "ids.txt").write_text("I10, 11\nD12 12\n13.0\n")
        r = run("ids_to_batches.py", self.tmp / "ids.txt", "--size", "2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("10,11", r.stdout)
        self.assertIn("12,13", r.stdout)

    def test_find_missing(self):
        (self.tmp / "want.txt").write_text("1\n2\n3\n")
        write_csv(self.tmp / "have.csv", [{"Image Data ID": "I1"}, {"Image Data ID": "I3"}, {"Image Data ID": "I9"}])
        r = run("find_missing_ids.py", self.tmp / "want.txt", self.tmp / "have.csv")
        self.assertEqual(r.stdout.split(), ["2"])
        self.assertIn("extra (not in wanted) 1", r.stderr)

    def test_select_one_per_visit(self):
        base = {"Subject ID": "000_S_0001", "Study Date": "1/1/2000", "Modality": "MRI"}
        rows = [
            {**base, "Description": "MPRAGE", "Image ID": "30"},
            {**base, "Description": "MPR; GradWarp; B1 Correction; N3; Scaled", "Image ID": "31"},
            {**base, "Description": "Localizer", "Image ID": "29"},
            {**base, "Study Date": "1/1/2001", "Description": "MPRAGE", "Image ID": "40"},
            {**base, "Study Date": "1/1/2001", "Description": "MPRAGE", "Image ID": "41"},
            {**base, "Study Date": "1/1/2002", "Description": "Localizer", "Image ID": "50"},
        ]
        write_csv(self.tmp / "s.csv", rows)
        r = run("select_one_per_visit.py", self.tmp / "s.csv", "--prefer", "GradWarp.*N3", "MPRAGE",
                "--strict", "--out", self.tmp / "o.csv", "--ids-out", self.tmp / "o.txt")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.tmp / "o.txt").read_text().split(), ["31", "40"])
        self.assertIn("tie", r.stdout)

    def test_check_zips(self):
        good = self.tmp / "zips"
        good.mkdir()
        with zipfile.ZipFile(good / "a.zip", "w") as z:
            z.writestr("x.txt", "hello" * 100)
        (good / "b.zip").write_bytes(b"not a zip")
        r = run("check_zips.py", good)
        self.assertEqual(r.returncode, 1)
        self.assertIn("1 OK, 1 FAILED", r.stdout)

    def test_index_images(self):
        d = self.tmp / "ADNI" / "000_S_0001" / "MPRAGE" / "2000-01-01_10_20_30.0" / "I123"
        d.mkdir(parents=True)
        (d / "a.dcm").write_bytes(b"")
        (d / "b.dcm").write_bytes(b"")
        r = run("index_images.py", self.tmp / "ADNI", "--out", self.tmp / "idx.csv")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(self.tmp / "idx.csv") as f:
            row = next(csv.DictReader(f))
        self.assertEqual((row["subject_id"], row["image_id"], row["acq_date"], row["n_files"], row["format"]),
                         ("000_S_0001", "123", "2000-01-01", "2", "dicom"))


if __name__ == "__main__":
    unittest.main()
