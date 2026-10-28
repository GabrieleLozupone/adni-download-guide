# 3. Choose the images you need

*Last verified: 28 October 2026. Descriptions and image types are the ones we saw in IDA on that date.*

ADNI contains tens of thousands of MRI and PET images, and **a single visit often has several images of the same
kind**: repeated scans, the same scan at several processing levels, localizers, other sequences. If you just tick
everything you get hundreds of GB you don't need, and duplicates that leak between train and test.

So decide a rule first. The usual one for deep learning is
**one image per participant × visit × modality**, chosen by an explicit preference.

## Words you need

- **Image ID**: IDA's number for one image (shown as `I000000` in folder names and as a plain number in tables).
- **Image type** (Advanced Search → IMAGE TYPES):
  - *Original*: as acquired, usually DICOM.
  - *Pre-processed*: corrected by ADNI teams (for example MRI GradWarp/B1/N3, PET averaging and standardization).
  - *Post-processed*: products derived from images, such as masks and segmentations.
- **Description**: the series name, for example `MPRAGE`, `Accelerated Sagittal MPRAGE`, or a processing chain such
  as `MPR; GradWarp; B1 Correction; N3; Scaled`.

## What to pick, by modality (a reasonable default)
**T1 MRI**

- ADNI1, ADNIGO, ADNI2: ADNI offers corrected versions (GradWarp, B1, N3). We received these as **NIfTI** (`.nii`).
- ADNI3, ADNI4: corrections are done on the scanner, so take the original images (DICOM), typically
  `Accelerated Sagittal MPRAGE` or the vendor equivalent.
- Background: ADNI's [MRI pre-processing page](https://adni.loni.usc.edu/data-samples/adni-data/neuroimaging/mri/mri-pre-processing/).

**PET (amyloid, tau, FDG)**

- ADNI provides several pre-processing levels. The most harmonized across scanners is usually the one whose
  description ends in `Uniform 6mm Res` (smoothed to a common resolution); then `Uniform Resolution`,
  `Std Img and Vox Siz`, `Co-registered, Averaged`, and finally the raw dynamic frames.
- Some recent (ADNI4) raw PET images are 4D (several frames). Pre-processed levels avoid that.

## Two ways to choose

### Way A: from the search results (simple)

1. IDA → **SEARCH** → **Advanced Image Search**.
2. Set: Project/Phase, **Modality**, **Image types**, and Description keywords (for example `MPRAGE`).
3. Under "Display in result", add the columns you want (Visit, Study Date, Description, Image ID, ...).
4. **SEARCH** → on the results tab click **CSV Download**. You now have a list of candidates.
5. Keep one image per participant/date/modality with your rule. The helper
   [`select_one_per_visit.py`](https://github.com/GabrieleLozupone/adni-download-guide/tree/main/scripts) does this from the CSV with a preference list you write:
   ```bash
   python scripts/select_one_per_visit.py search_results.csv \
       --prefer "GradWarp.*N3" "Accelerated Sagittal MPRAGE" "MPRAGE" \
       --out selected.csv
   ```

6. Then add the chosen Image IDs to a collection ([step 4](04-collection-and-download.md)).

### Way B: from ADNI's own quality and analysis tables (better)
ADNI teams have already chosen, checked and analysed one image for most visits. Their tables include the **Image ID
they used**, so you can reuse their choice:

| Table ([Study Data](02-tabular-data.md)) | Image ID column | Use |
| --- | --- | --- |
| `ADSP_PHC_T1_FS` / `ADSP_PHC_T1_MUSE` | `PHC_LONIUID` | Harmonized T1 per visit (visually QC'd) |
| `UCSFFSX7` | `IMAGEUID` | T1 processed with FreeSurfer 7; drop rows where `OVERALLQC` = Fail |
| `MRIQC` | `LONIImage` (also `image_id`) | Every MRI series with `SeriesType` (T1w, ...) for your own rule |
| `MAYOADIRL_MRI_QUALITY_ADNI3` | `LONI_IMAGE` | ADNI3 series quality and a `SERIES_SELECTED` flag |
| PET analysis tables (UC Berkeley, ...) | see each table's PDF | PET images already processed and QC'd |

Read the PDF next to each table before relying on it. Merge the Image IDs with your visit table (on `RID`/`PTID` and
dates), keep one per visit, and you have your list.

## Search by Image ID
Advanced Image Search has an **Image ID** box that accepts a comma-separated list. Our notes:

- Tick **all the modalities** your IDs belong to (MRI and PET) and **all the image types** (Original, Pre-processed,
  Post-processed). Otherwise some IDs silently return nothing.
- Work in batches: we used up to 1,000 IDs per search. [`ids_to_batches.py`](https://github.com/GabrieleLozupone/adni-download-guide/tree/main/scripts) splits a long list into
  ready-to-paste lines.
- Compare the number of results with the number of IDs you pasted. If it's lower, some IDs are not available to your
  account, belong to an unticked modality/type, or were mistyped.

## Before downloading: how big will it be?

- In our download (October 2026), about 34,000 images (T1 + PET + masks) took about **313 GB** as ZIP files, roughly
  9 MB per image on average. Sizes vary a lot by modality and phase.
- IDA shows the size of each ZIP before you download it ([step 4](04-collection-and-download.md)).

## Shortcut for beginners
IDA → Data Collections → **Other Shared Collections** contains standardized collections created by the study leaders
and available to all ADNI users. Look there first: if one fits your need, you can download it without building your
own.

Next: [4. Build a collection and download it](04-collection-and-download.md)
