#!/usr/bin/env python3
"""Convert IDA image downloads (the ZIPs, or the folders unpacked from them) into a BIDS dataset.

    python scripts/ida_to_bids.py /path/to/ADNI_zips --bids /path/to/ADNI_bids \\
        --metadata search_results.csv [--only-ids wanted_ids.txt] [--jobs 4] [--dry-run]

SOURCE can be a folder of ZIPs (read directly, no need to unpack), a single ZIP, or an unpacked folder. IDA lays
images out as <Project>/<Subject ID>/<Description>/<YYYY-MM-DD_hh_mm_ss.f>/I<Image ID>/<files>, so this works for
ADNI, AIBL and other IDA projects. Naming:

    sub-<Project><Subject ID without _>/ses-<acquisition date YYYYMMDD>/
        anat/..._T1w.nii.gz | _FLAIR | _T2w          MRI, from the Description
        pet/..._trc-<tracer>_rec-<level>_pet.nii.gz  PET; tracer from the Description or from --metadata
    derivatives/ida/sub-.../ses-.../anat/..._desc-brain_mask.nii.gz | _dseg   masks and segmentations from IDA
    code/ida_to_bids/images.tsv     one row per Image ID: what it became, why, grid, orientation, sha256
    participants.tsv, dataset_description.json

The conversion is faithful: no resampling, no reorientation. DICOM goes through dcm2niix, NIfTI from IDA is only
compressed. The JSON sidecar keeps the dcm2niix fields plus IDA_ImageID, IDA_Description and IDA_SubjectID. Two
images that would get the same name (repeats in one visit) get run-1, run-2: select one per visit before training.

--metadata: one or more CSVs exported from IDA (Advanced Search results or a collection). Its Modality, Type and
"Imaging Protocol" columns make the classification safer; for PET the tracer often appears only in "Imaging Protocol"
(add it under "Display in result"). Without it, PET with no tracer in the Description gets trc-unknown.
--rules: a TSV of your own "pattern<TAB>target" lines, checked before the built-in ones. pattern is a regex on the
Description; target is anat/T1w, anat/T2w, anat/FLAIR, anat/PDw, pet, mask, dseg or skip.

Run it again to resume: images already converted are skipped. Prints counts only. Requires Python 3.8+ and dcm2niix.
Downloaded files are untrusted: only paths matching the IDA layout are read, and they are written under fixed names.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from _ids import find_id_column, normalize_id, read_csv_rows, read_ids

LAYOUT = re.compile(r"^(?P<project>[^/]+)/(?P<subject>[^/]+)/(?P<desc>[^/]+)/(?P<date>\d{4}-\d{2}-\d{2})_(?P<time>[^/]*)"
                    r"/(?P<folder>[ID]\d+)/(?P<file>[^/]+)$")
TRACERS = [  # (regex on Description or Radiopharmaceutical, BIDS label)
    (r"AV-?45|florbetapir", "AV45"), (r"FBB|florbetaben", "FBB"), (r"PIB|PiB", "PIB"), (r"NAV-?4694", "NAV4694"),
    (r"AV-?1451|flortaucipir", "AV1451"), (r"MK-?6240", "MK6240"), (r"PI-?2620", "PI2620"), (r"FDG", "FDG"),
]
PET_LEVELS = [  # ADNI PET pre-processing levels, most harmonized first
    (r"Uniform 6mm Res", "6mm"), (r"Uniform Resolution", "uniformres"),
    (r"Std Img and Vox Siz|Standardized Image and Voxel Size", "stdimgvox"),
    (r"Co-?reg(istered)?,? (Avg|Averaged)", "coregavg"), (r"Co-?reg(istered)?,? Dyn", "coregdyn"),
]
DEFAULT_RULES = [  # (regex on Description, target), first match wins
    (r"localizer|scout|calibration|survey|3-?plane", "skip"),
    (r"mask", "mask"),
    (r"segment|label|MUSE|FreeSurfer|aseg", "dseg"),
    (r"FLAIR", "anat/FLAIR"),
    (r"\bPD\b|proton density", "anat/PDw"),
    (r"T2|TSE|FSE", "anat/T2w"),
    (r"MPRAGE|MP-RAGE|MPR\b|SPGR|IR-?F?SPGR|\bT1|MT1", "anat/T1w"),
]
PET_HINT = re.compile(r"\bPET\b|Co-?reg|Uniform|Radiopharm|" + "|".join(rx for rx, _ in TRACERS), re.I)


def label(s):
    return re.sub(r"[^A-Za-z0-9]", "", str(s))


# ----------------------------------------------------------------------------- finding images

def find_images(sources):
    """Image ID -> dict(project, subject, desc, date, time, members=[(zip or None, path)]). First source wins."""
    images = {}

    def add(m, zpath, member):
        iid = normalize_id(m["folder"])
        img = images.setdefault(iid, dict(project=m["project"], subject=m["subject"],
                                          desc=m["desc"].replace("_", " "), date=m["date"],
                                          time=m["time"].replace("_", ":"), folder=m["folder"], members=[]))
        if (img["project"], img["subject"], img["folder"]) == (m["project"], m["subject"], m["folder"]):
            img["members"].append((zpath, member))

    for src in map(Path, sources):
        zips = [src] if src.suffix.lower() == ".zip" else sorted(src.glob("*.zip"))
        if zips:
            for z in zips:
                with zipfile.ZipFile(z) as zf:
                    for info in zf.infolist():
                        m = LAYOUT.match(info.filename)
                        if m and not info.is_dir():
                            add(m, str(z), info.filename)
        else:
            for dirpath, _, filenames in os.walk(src):
                parts = Path(dirpath).parts
                if len(parts) < 5 or not re.fullmatch(r"[ID]\d+", parts[-1]):
                    continue
                for f in sorted(filenames):
                    m = LAYOUT.match("/".join(parts[-5:] + (f,)))
                    if m:
                        add(m, None, os.path.join(dirpath, f))
    return images


def load_metadata(paths):
    meta = {}
    for p in paths or []:
        fieldnames, rows = read_csv_rows(p)
        col = find_id_column(fieldnames)
        for r in rows:
            iid = normalize_id(r.get(col, ""))
            if iid:
                meta.setdefault(iid, r)
    return meta


# ----------------------------------------------------------------------------- naming

def classify(img, meta, rules):
    """-> (target, tracer, level, note)."""
    desc = img["desc"]
    modality = (meta.get("Modality") or "").upper()
    protocol = meta.get("Imaging Protocol") or ""
    radio = re.search(r"Radiopharmaceutical=([^;]+)", protocol)
    is_pet = modality == "PET" or (not modality and bool(PET_HINT.search(desc)))
    for rx, target in rules:
        if re.search(rx, desc, re.I):
            if target in ("mask", "dseg", "skip") or not is_pet:
                return target, None, None, ""
            break
    if not is_pet:
        return "unclassified", None, None, "no rule matched the Description"
    tracer = next((t for rx, t in TRACERS if re.search(rx, desc, re.I)), None)
    if radio and not tracer:
        tracer = next((t for rx, t in TRACERS if re.search(rx, radio.group(1), re.I)), label(radio.group(1)))
    if re.search(r"\bEarly\b", desc, re.I) and tracer:
        tracer += "early"
    level = next((name for rx, name in PET_LEVELS if re.search(rx, desc, re.I)), None)
    if not level and ((meta.get("Type") or "").lower() == "original" or re.search(r"\braw\b", desc, re.I)):
        level = "raw"
    return "pet", tracer or "unknown", level, "" if tracer else "tracer unknown: pass --metadata with Imaging Protocol"


def plan(images, meta, rules):
    rows = []
    for iid, img in images.items():
        target, tracer, level, note = classify(img, meta.get(iid, {}), rules)
        sub = "sub-" + label(img["project"] + img["subject"])
        ses = "ses-" + img["date"].replace("-", "")
        stem = f"{sub}_{ses}"
        if target.startswith("anat/"):
            path, suffix = f"{sub}/{ses}/anat/{stem}", target.split("/")[1]
        elif target == "pet":
            path, suffix = f"{sub}/{ses}/pet/{stem}_trc-{tracer}" + (f"_rec-{level}" if level else ""), "pet"
        elif target in ("mask", "dseg"):
            path = f"derivatives/ida/{sub}/{ses}/anat/{stem}"
            suffix = "desc-brain_mask" if target == "mask" else "dseg"
        else:
            path, suffix = None, None
        rows.append(dict(image_id=iid, project=img["project"], subject_id=img["subject"], description=img["desc"],
                         acq_date=img["date"], acq_time=img["time"], target=target, tracer=tracer or "",
                         level=level or "", participant_id=sub, _path=path, _suffix=suffix, note=note))
    # same name for several images (repeats in one visit) -> run-<k>, ordered by time then Image ID
    groups = defaultdict(list)
    for r in rows:
        if r["_path"]:
            groups[(r["_path"], r["_suffix"])].append(r)
    for (path, suffix), rs in groups.items():
        rs.sort(key=lambda r: (r["acq_time"], int(r["image_id"])))
        for k, r in enumerate(rs, 1):
            run = f"_run-{k}" if len(rs) > 1 else ""
            r["bids_path"] = f"{path}{run}_{suffix}.nii.gz"
            r["n_same_name"] = len(rs)
    return rows


# ----------------------------------------------------------------------------- converting one image

def nifti_header(path):
    """Shape, voxel size and orientation (axis codes from the sform/qform rotation) from a .nii.gz header."""
    with gzip.open(path, "rb") as f:
        h = f.read(348)
    end = "<" if struct.unpack("<i", h[:4])[0] == 348 else ">"
    dim = struct.unpack(end + "8h", h[40:56])
    pixdim = struct.unpack(end + "8f", h[76:108])
    qform, sform = struct.unpack(end + "2h", h[252:256])
    if sform > 0:
        rot = [struct.unpack(end + "4f", h[280 + 16 * i:296 + 16 * i])[:3] for i in range(3)]
    else:
        b, c, d = struct.unpack(end + "3f", h[256:268])
        a = max(0.0, 1.0 - (b * b + c * c + d * d)) ** 0.5
        rot = [[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
               [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
               [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - c * c - b * b]]
        if pixdim[0] < 0:
            rot = [[row[0], row[1], -row[2]] for row in rot]
    codes = ""
    for j in range(3):
        col = [rot[i][j] for i in range(3)]
        i = max(range(3), key=lambda k: abs(col[k]))
        codes += ("LR", "PA", "IS")[i][col[i] > 0]
    ndim = dim[0]
    return dict(shape="x".join(map(str, dim[1:1 + ndim])), ndim=ndim,
                voxel_mm="x".join(f"{v:.3g}" for v in pixdim[1:4]), orientation=codes)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def convert_one(job):
    """One Image ID -> one .nii.gz + .json in the BIDS tree. Returns a result dict."""
    iid, members, dst, tmp_root, sidecar_extra = job
    res = dict(image_id=iid)
    tmp = Path(tempfile.mkdtemp(prefix=f"img{iid}_", dir=tmp_root))
    try:
        src = tmp / "src"
        src.mkdir()
        open_zips = {}
        for k, (zpath, name) in enumerate(members):  # fixed local names: nothing from the download decides a path
            suffix = ".nii.gz" if name.lower().endswith(".nii.gz") else Path(name).suffix.lower()
            with open(src / f"f{k:05d}{suffix}", "wb") as out:
                if zpath:
                    zf = open_zips.setdefault(zpath, zipfile.ZipFile(zpath))
                    with zf.open(name) as a:
                        shutil.copyfileobj(a, out)
                else:
                    with open(name, "rb") as a:
                        shutil.copyfileobj(a, out)
        for zf in open_zips.values():
            zf.close()
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        nii = sorted(src.glob("*.nii*"))
        sidecar = {}
        if nii:
            if nii[0].name.endswith(".gz"):
                shutil.copy(nii[0], dst)
            else:
                with open(nii[0], "rb") as a, gzip.open(dst, "wb", compresslevel=6) as b:
                    shutil.copyfileobj(a, b)
            res.update(conversion="nifti_from_ida", n_outputs=len(nii))
        else:
            out = tmp / "out"
            out.mkdir()
            r = subprocess.run(["dcm2niix", "-z", "y", "-b", "y", "-ba", "y", "-f", "img_%s", "-o", str(out), str(src)],
                               capture_output=True, text=True)
            made = sorted(out.glob("*.nii.gz"), key=lambda p: p.stat().st_size, reverse=True)
            if not made:
                res.update(conversion="dcm2niix_failed", note=(r.stdout + r.stderr)[-300:].replace("\n", " "))
                return res
            shutil.move(str(made[0]), str(dst))  # the largest output is the image; any others are counted, not kept
            js = made[0].with_name(made[0].name[:-len(".nii.gz")] + ".json")
            if js.exists():
                sidecar = json.loads(js.read_text())
            res.update(conversion="dcm2niix" + ("_warning" if "Warning" in r.stdout else ""), n_outputs=len(made))
        sidecar.update(sidecar_extra)
        Path(str(dst)[:-len(".nii.gz")] + ".json").write_text(json.dumps(sidecar, indent=1))
        res.update(nifti_header(dst), nii_bytes=dst.stat().st_size, sha256=sha256(dst))
    except Exception as ex:  # one bad image must not stop the others
        res.update(conversion="error", note=f"{type(ex).__name__}: {ex}"[:300])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


# ----------------------------------------------------------------------------- main

def write_tsv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sources", nargs="+", help="folders of ZIPs, ZIP files, or unpacked folders")
    p.add_argument("--bids", required=True, help="output BIDS folder (created if needed)")
    p.add_argument("--metadata", nargs="*", help="CSV exported from IDA (search results or collection)")
    p.add_argument("--rules", help="TSV of extra 'pattern<TAB>target' rules, checked first")
    p.add_argument("--only-ids", help="convert only these Image IDs (text list or CSV)")
    p.add_argument("--name", default="IDA images converted to BIDS", help="Name in dataset_description.json")
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--tmp", help="folder for temporary files (default: system temp)")
    p.add_argument("--dry-run", action="store_true", help="only write the planned images.tsv and print counts")
    a = p.parse_args()

    rules = list(DEFAULT_RULES)
    if a.rules:
        with open(a.rules, encoding="utf-8") as f:
            extra = [line.rstrip("\n").split("\t") for line in f if line.strip() and not line.startswith("#")]
        rules = [(x[0], x[1].strip()) for x in extra] + rules
    bids = Path(a.bids)
    code = bids / "code" / "ida_to_bids"
    code.mkdir(parents=True, exist_ok=True)

    images = find_images(a.sources)
    if a.only_ids:
        wanted = set(read_ids(a.only_ids))
        print(f"--only-ids: {len(wanted)} wanted, {len(wanted & set(images))} found in the sources, "
              f"{len(wanted - set(images))} missing")
        images = {i: v for i, v in images.items() if i in wanted}
    if not images:
        sys.exit("No images found. Expected the IDA layout <Project>/<Subject>/<Description>/<date_time>/I<id>/...")
    meta = load_metadata(a.metadata)
    rows = plan(images, meta, rules)
    if a.metadata:
        print(f"metadata found for {sum(r['image_id'] in meta for r in rows)} of {len(rows)} images")
    print(f"{len(rows)} images, {len({r['participant_id'] for r in rows})} subjects")
    print("targets: " + ", ".join(f"{k} {v}" for k, v in Counter(r["target"] for r in rows).most_common()))
    pet = [r for r in rows if r["target"] == "pet"]
    if pet:
        print("PET tracers: " + ", ".join(f"{k} {v}" for k, v in Counter(r["tracer"] for r in pet).most_common()))

    done_file = code / "results.jsonl"
    done = {}
    if done_file.exists():
        for line in done_file.read_text().splitlines():
            r = json.loads(line)
            done[r["image_id"]] = r
    fields = ["image_id", "project", "subject_id", "participant_id", "description", "acq_date", "acq_time", "target",
              "tracer", "level", "bids_path", "n_same_name", "status", "conversion", "n_outputs", "shape", "ndim",
              "voxel_mm", "orientation", "nii_bytes", "sha256", "note"]
    # an image already converted keeps its first name, even if new --metadata or --rules would name it differently
    renamed = 0
    for r in rows:
        prev = done.get(r["image_id"], {})
        if r.get("bids_path") and prev.get("sha256") and (bids / prev["bids_path"]).exists():
            renamed += prev["bids_path"] != r["bids_path"]
            r["bids_path"], r["_done"] = prev["bids_path"], True
    if renamed:
        print(f"{renamed} images already converted would now get another name: kept the old one "
              f"(delete the output folder to start again)")
    todo = [r for r in rows if r.get("bids_path") and not r.get("_done")]
    print(f"to convert: {len(todo)}, already done: {sum(1 for r in rows if r.get('bids_path')) - len(todo)}, "
          f"not converted (skip/unclassified): {sum(1 for r in rows if not r.get('bids_path'))}")
    repeats = sum(1 for r in rows if r.get("n_same_name", 1) > 1)
    if repeats:
        print(f"{repeats} images share a name with another one of the same visit and got run-<k>")
    if a.dry_run:
        write_tsv(code / "images_planned.tsv", sorted(rows, key=lambda r: r.get("bids_path") or ""), fields)
        print(f"plan written to {code / 'images_planned.tsv'} (nothing converted)")
        return
    if todo and not shutil.which("dcm2niix"):
        print("warning: dcm2niix not found; only images that IDA already gives as NIfTI can be converted",
              file=sys.stderr)

    jobs = []
    for r in todo:
        img = images[r["image_id"]]
        extra = dict(IDA_ImageID=img["folder"], IDA_Project=img["project"], IDA_SubjectID=img["subject"],
                     IDA_Description=img["desc"], IDA_AcquisitionDateTime=f"{img['date']} {img['time']}")
        if r["target"] == "pet":
            extra.update(TracerName=r["tracer"], IDA_Level=r["level"] or None)
        m = meta.get(r["image_id"], {})
        for col in ("Modality", "Type", "Imaging Protocol"):
            if m.get(col):
                extra["IDA_" + label(col)] = m[col]
        extra = {k: v for k, v in extra.items() if v is not None}
        jobs.append((r["image_id"], img["members"], str(bids / r["bids_path"]), a.tmp, extra))
    path_of = {r["image_id"]: r["bids_path"] for r in todo}
    with open(done_file, "a") as log, ProcessPoolExecutor(a.jobs) as ex:
        futures = [ex.submit(convert_one, j) for j in jobs]
        for k, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            res["bids_path"] = path_of[res["image_id"]]
            done[res["image_id"]] = res
            log.write(json.dumps(res) + "\n")
            log.flush()
            if k % 100 == 0 or k == len(futures):
                print(f"  {k}/{len(futures)}", flush=True)

    for r in rows:
        res = done.get(r["image_id"], {}) if r.get("bids_path") else {}
        r.update({k: v for k, v in res.items() if k != "image_id"})
        r["status"] = ("converted" if res.get("sha256") else "failed") if r.get("bids_path") else r["target"]
    rows.sort(key=lambda r: r.get("bids_path") or "~" + r["image_id"])
    write_tsv(code / "images.tsv", rows, fields)

    ok = [r for r in rows if r["status"] == "converted"]
    subjects = sorted({(r["participant_id"], r["project"], r["subject_id"]) for r in ok})
    write_tsv(bids / "participants.tsv", [dict(participant_id=s, project=p_, subject_id=i) for s, p_, i in subjects],
              ["participant_id", "project", "subject_id"])
    (bids / "dataset_description.json").write_text(json.dumps({
        "Name": a.name, "BIDSVersion": "1.9.0", "DatasetType": "raw",
        "GeneratedBy": [{"Name": "ida_to_bids.py", "CodeURL": "https://github.com/GabrieleLozupone/adni-download-guide"}],
        "SourceDatasets": [{"URL": "https://ida.loni.usc.edu"}]}, indent=1))
    if any(r["target"] in ("mask", "dseg") for r in ok):
        (bids / "derivatives" / "ida" / "dataset_description.json").write_text(json.dumps({
            "Name": "Derived images distributed by IDA (masks, segmentations)", "BIDSVersion": "1.9.0",
            "DatasetType": "derivative", "GeneratedBy": [{"Name": "as distributed by IDA"}]}, indent=1))

    print(f"\nconverted {len(ok)}, failed {sum(r['status'] == 'failed' for r in rows)}, "
          f"subjects {len(subjects)} -> {bids}")
    print("conversion: " + ", ".join(f"{k} {v}" for k, v in Counter(r.get("conversion") for r in ok).most_common()))
    print("orientation: " + ", ".join(f"{k} {v}" for k, v in Counter(r.get("orientation") for r in ok).most_common()))
    n4d = sum(1 for r in ok if int(r.get("ndim") or 3) > 3)
    if n4d:
        print(f"{n4d} images are 4D (several frames, usually PET): average them or use a pre-processed level")
    print(f"details per image: {code / 'images.tsv'}")
    sys.exit(1 if any(r["status"] == "failed" for r in rows) else 0)


if __name__ == "__main__":
    main()
