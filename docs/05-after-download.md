# 5. After the download: check, unpack, convert

*Last verified: 28 October 2026, on our own download (ADNI1 to ADNI4, T1 MRI, PET and masks).*

## 1. Test every ZIP before anything else
IDA ZIPs are often larger than 4 GB, so they use the **Zip64** format. Some tools (older `unzip` builds, some
graphical archive managers) fail on them. These work: Info-ZIP `unzip` 6.0, `7z`, Python's `zipfile`.

```bash
python scripts/check_zips.py /path/to/ADNI_zips        # tests every ZIP, prints OK/FAILED
# or by hand:
unzip -tq file.zip
```
Download any FAILED ZIP again. Keep the ZIPs as your untouched raw copy, ideally read-only.

## 2. Unpack

```bash
mkdir -p /path/to/ADNI_raw
for z in /path/to/ADNI_zips/*.zip; do unzip -q -n "$z" -d /path/to/ADNI_raw; done
```
The layout inside is:

```
ADNI/<Subject ID>/<Description>/<YYYY-MM-DD_hh_mm_ss.f>/I<Image ID>/<files .dcm or .nii>
     000_S_0000 /  MPRAGE     /  2000-01-01_00_00_00.0 / I000000 / ...   (made-up example)
```
The ZIPs contain **no metadata table**. Subject, description, date and Image ID are only in the folder path. Build an
index:

```bash
python scripts/index_images.py /path/to/ADNI_raw/ADNI --out image_index.csv
```
`image_index.csv` has one row per image: subject, description, acquisition date and time, Image ID, number of files,
format, and path. Check its Image IDs against your wanted list:

```bash
python scripts/find_missing_ids.py wanted_ids.txt image_index.csv
```

## 3. Convert DICOM to NIfTI
What we received:

| Images | Format in the ZIP |
| --- | --- |
| T1 ADNI1/GO/2, pre-processed (GradWarp/B1/N3) | NIfTI `.nii` |
| T1 ADNI3/4, original | DICOM |
| PET, all phases | DICOM |
| Brain masks (derived products) | NIfTI |

Convert DICOM with [dcm2niix](https://github.com/rordenlab/dcm2niix), naming each output by its Image ID:

```bash
bash scripts/convert_to_nifti.sh /path/to/ADNI_raw/ADNI /path/to/ADNI_nifti
```
Warnings about slice spacing or missing fields are common. Check a few images visually before trusting a batch.

### Or: straight to BIDS
[BIDS](https://bids.neuroimaging.io/) is the folder layout most neuroimaging tools read (FastSurfer, fMRIPrep,
Clinica, ...). `ida_to_bids.py` reads the ZIPs directly (no need to unpack) or the unpacked folders:

```bash
python scripts/ida_to_bids.py /path/to/ADNI_zips --bids /path/to/ADNI_bids \
    --metadata search_results.csv --jobs 4 --dry-run     # check the plan first, then run without --dry-run
```
What you get:

```
ADNI_bids/
  sub-ADNI000S0000/ses-20000101/anat/sub-ADNI000S0000_ses-20000101_T1w.nii.gz (+ .json)   (made-up example)
  sub-ADNI000S0000/ses-20000301/pet/sub-ADNI000S0000_ses-20000301_trc-AV45_rec-6mm_pet.nii.gz
  derivatives/ida/sub-.../anat/..._desc-brain_mask.nii.gz       masks and segmentations from IDA
  participants.tsv  dataset_description.json
  code/ida_to_bids/images.tsv                                   one row per Image ID
```
- **Subject** = project + Subject ID (`000_S_0000` → `sub-ADNI000S0000`); **session** = the acquisition date, which
  avoids the ambiguity of visit codes. Link sessions to clinical visits by date (section 5 below).
- **MRI type** comes from the Description (MPRAGE, SPGR → `T1w`; FLAIR; T2). Localizers and calibrations are skipped;
  anything unrecognised is listed as `unclassified` in `images.tsv`. Add your own rules with `--rules`.
- **PET tracer**: ADNI pre-processed PET descriptions often don't name the tracer. Pass the CSV of your search or
  collection with the **Imaging Protocol** column (add it under "Display in result"), or you get `trc-unknown`.
  `rec-` is the ADNI processing level (`6mm`, `uniformres`, `stdimgvox`, `coregavg`, `raw`).
- **Repeats** in one visit get `run-1`, `run-2`. Better: select one image per visit before downloading (step 3).
- The conversion is faithful (no resampling, no reorientation). `images.tsv` records shape, voxel size, orientation
  and 4D images, so the traps below are easy to find. Run the same command again to resume.
- Each `.json` sidecar keeps the dcm2niix fields plus `IDA_ImageID`, `IDA_SubjectID`, `IDA_Description`, so every file
  can be traced back to IDA and to the tables.

Check the result with the [BIDS validator](https://bids-standard.github.io/bids-validator/) (it runs locally in your
browser or from the command line; the files are not uploaded).

## 4. Traps we found in the images

- **Mixed orientations** across phases and modalities. Reorient everything to one convention before training, for
  example with `nibabel.as_closest_canonical`.
- **Masks can have a different origin from their T1.** In one phase the header origin differed by about 500 mm even
  though the voxel grid was the same. Apply a mask voxel by voxel after checking that the shapes match; don't rely on
  world coordinates.
- **Some PET images are 4D** (several frames). Average the frames, or download a pre-processed level instead.
- **Repeated scans**: if you didn't select one image per visit before downloading, do it now, before any split.

## 5. Connect images to the clinical tables

1. Subject ID (`PTID`) → `RID` with the `ROSTER` table.
2. Image ID → the analysis or QC tables you used to choose images (`IMAGEUID`, `PHC_LONIUID`, `LONIImage`, ...).
3. Acquisition date → nearest clinical visit of the same `RID`. Keep the difference in days and set a maximum
   (for example 90 days).
4. Split train/validation/test **by `RID`**. Then fit any normalization or preprocessing statistics on the training set
   only.

## 6. Where to keep the data

- Only your team should be able to read the storage (DUA).
- Keep data out of your Git repository. A `.gitignore` with `*.zip`, `*.nii*`, `*.dcm`, `data/` helps.
- Write down the download date and collection names next to the data.

Next: [Troubleshooting](06-troubleshooting.md)
