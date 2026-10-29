"""Tests on synthetic, made-up data only (no ADNI data)."""
import csv
import json
import struct
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

    def _ida_zip(self):
        """A made-up IDA ZIP: T1 (two repeats on one date), PET, brain mask, localizer, all as tiny NIfTI."""
        zdir = self.tmp / "zips"
        zdir.mkdir()
        items = [("MPRAGE", "2000-01-01_10_00_00.0", "I11", (4, 5, 6)),
                 ("MPRAGE", "2000-01-01_10_30_00.0", "I12", (4, 5, 6)),
                 ("AV45_Coreg,_Avg,_Std_Img_and_Vox_Siz,_Uniform_Resolution", "2000-02-03_09_00_00.0", "I20", (4, 4, 4, 2)),
                 ("Coreg,_Avg,_Std_Img_and_Vox_Siz,_Uniform_6mm_Res", "2000-02-04_09_00_00.0", "I21", (4, 4, 4)),
                 ("PHC_Brain_Mask", "2000-01-01_10_00_00.0", "D30", (4, 5, 6)),
                 ("Localizer", "2000-01-01_09_50_00.0", "I40", (4, 5, 6))]
        with zipfile.ZipFile(zdir / "a.zip", "w") as z:
            for desc, stamp, folder, shape in items:
                z.writestr(f"ADNI/000_S_0001/{desc}/{stamp}/{folder}/img.nii", tiny_nifti(shape))
            z.writestr("../evil.txt", "ignored: not the IDA layout")
        return zdir

    def test_ida_to_bids(self):
        zdir = self._ida_zip()
        write_csv(self.tmp / "meta.csv", [{"Image ID": "21", "Modality": "PET", "Type": "Pre-processed",
                                           "Imaging Protocol": "Radiopharmaceutical=18F-FDG; Frames=1"}])
        bids = self.tmp / "bids"
        r = run("ida_to_bids.py", zdir, "--bids", bids, "--metadata", self.tmp / "meta.csv", "--jobs", "1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        sub = bids / "sub-ADNI000S0001"
        self.assertTrue((sub / "ses-20000101/anat/sub-ADNI000S0001_ses-20000101_run-1_T1w.nii.gz").exists())
        self.assertTrue((sub / "ses-20000101/anat/sub-ADNI000S0001_ses-20000101_run-2_T1w.json").exists())
        self.assertTrue((sub / "ses-20000203/pet/sub-ADNI000S0001_ses-20000203_trc-AV45_rec-uniformres_pet.nii.gz").exists())
        self.assertTrue((sub / "ses-20000204/pet/sub-ADNI000S0001_ses-20000204_trc-FDG_rec-6mm_pet.nii.gz").exists())
        self.assertTrue((bids / "derivatives/ida/sub-ADNI000S0001/ses-20000101/anat/"
                                "sub-ADNI000S0001_ses-20000101_desc-brain_mask.nii.gz").exists())
        self.assertFalse((self.tmp / "evil.txt").exists())
        with open(bids / "code/ida_to_bids/images.tsv") as f:
            rows = {x["image_id"]: x for x in csv.DictReader(f, delimiter="\t")}
        self.assertEqual(rows["40"]["status"], "skip")
        self.assertEqual((rows["11"]["shape"], rows["11"]["orientation"]), ("4x5x6", "RAS"))
        self.assertEqual(rows["20"]["ndim"], "4")
        sidecar = json.loads((sub / "ses-20000101/anat/sub-ADNI000S0001_ses-20000101_run-1_T1w.json").read_text())
        self.assertEqual(sidecar["IDA_ImageID"], "I11")
        self.assertIn("converted 5, failed 0", r.stdout)
        again = run("ida_to_bids.py", zdir, "--bids", bids, "--jobs", "1")
        self.assertIn("to convert: 0", again.stdout)

    def test_ida_to_bids_unpacked_and_dry_run(self):
        zdir = self._ida_zip()
        raw = self.tmp / "raw"
        with zipfile.ZipFile(zdir / "a.zip") as z:
            z.extractall(raw, members=[n for n in z.namelist() if n.startswith("ADNI/")])
        r = run("ida_to_bids.py", raw / "ADNI", "--bids", self.tmp / "b2", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("6 images, 1 subjects", r.stdout)
        self.assertIn("unknown 1", r.stdout)  # PET without tracer in the Description and no --metadata
        self.assertFalse(list((self.tmp / "b2").glob("sub-*")))


def tiny_nifti(shape):
    """Uncompressed NIfTI-1 with an identity sform (RAS), 1 mm voxels, uint8 zeros."""
    hdr = bytearray(352)
    struct.pack_into("<i", hdr, 0, 348)
    struct.pack_into("<8h", hdr, 40, len(shape), *shape, *[1] * (7 - len(shape)))
    struct.pack_into("<hh", hdr, 70, 2, 8)  # datatype uint8, bitpix
    struct.pack_into("<8f", hdr, 76, 1, 1, 1, 1, 1, 0, 0, 0)
    struct.pack_into("<f", hdr, 108, 352)
    struct.pack_into("<hh", hdr, 252, 0, 1)  # qform_code 0, sform_code 1
    for i in range(3):
        row = [0.0] * 4
        row[i] = 1.0
        struct.pack_into("<4f", hdr, 280 + 16 * i, *row)
    hdr[344:348] = b"n+1\0"
    n = 1
    for s in shape:
        n *= s
    return bytes(hdr) + bytes(n)


if __name__ == "__main__":
    unittest.main()
