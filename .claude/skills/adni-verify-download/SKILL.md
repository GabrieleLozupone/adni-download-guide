---
name: adni-verify-download
description: Help the user verify a finished ADNI/IDA download — test the ZIPs, unpack, index, compare with the wanted Image IDs and convert to NIfTI — using only summary counts the user pastes back. Use after ZIPs are downloaded or when the user suspects missing or corrupted files.
---

# Verify an ADNI download

The user runs every command; you read only the summary lines they paste. Never open their data, indexes or ID lists
(see `AGENTS.md`). Reference: `docs/05-after-download.md`.

## Steps (one at a time, wait for each result)
1. **Test the ZIPs**
   `python scripts/check_zips.py /path/to/zips` → ask for the last line (`N OK, M FAILED`) and the names of FAILED
   ZIPs. ZIP names are not participant data. If anything failed, re-download only those ZIPs (`download_urls.sh`
   skips finished ones; expired links must be regenerated in IDA).
2. **Unpack** into a separate folder:
   `for z in /path/to/zips/*.zip; do unzip -q -n "$z" -d /path/to/raw; done`
   If unzip complains about the format, use `7z x` (Zip64).
3. **Index**
   `python scripts/index_images.py /path/to/raw/ADNI --out image_index.csv` → ask for the summary (images, subjects,
   formats, duplicate warning).
4. **Compare with what they wanted**
   `python scripts/find_missing_ids.py wanted_ids.txt image_index.csv > missing.txt` → ask for the summary line only.
   If images are missing, they re-add `missing.txt` to the collection (`docs/04-collection-and-download.md`) and
   download again.
5. **Convert** (needs dcm2niix)
   `bash scripts/convert_to_nifti.sh /path/to/raw/ADNI /path/to/nifti` → ask for the final counts. If some failed,
   they look at `conversion_errors.txt` themselves. You can explain dcm2niix messages they paraphrase.
6. **Remind** the known image traps from `docs/05-after-download.md` (mixed orientations, mask origins, 4D PET,
   repeated scans), the split-by-RID rule, and to record the download date. Update `.adni-progress.md`.

## Interpreting counts
- Indexed images > wanted: they downloaded extra images (other subset or old collection), so they should filter by the
  wanted list.
- Indexed images < wanted with all ZIPs OK: images are missing from the collection, not broken.
- Format `other`/`empty`: an unusual product. Ask the user to describe the folder contents (file extensions only).
