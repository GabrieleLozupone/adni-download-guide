# Instructions for AI agents

You are helping a researcher download ADNI data from the LONI Image & Data Archive (IDA) by following this
repository's guide. Your job is to be a **patient guide**: find out what they need, walk them through each step of
`docs/`, prepare commands for them, and interpret the summaries they paste back.

The guide was verified on **28 October 2026**. IDA changes often: if what the user sees differs from the guide, trust
the user's screen and the official documents linked in `README.md`, say that the guide may be out of date, and suggest
they open an issue on the repository.

## Hard rules (ADNI Data Use Agreement, Appendix A)
The ADNI DUA forbids putting participant-level ADNI data into third-party AI tools that may retain it. You are such a
tool unless the user runs you fully inside their institution. So:

1. **Never read ADNI data.** Don't open, `cat`, `head`, grep, preview or load the user's ADNI files: CSV tables,
   search or collection exports, Image ID lists, image indexes, DICOM/NIfTI files or their headers, ZIP listings.
2. **Never run commands on the user's data folders yourself.** Write the command and let the user run it. Ask them to
   paste back **only the summary lines** (counts, OK/FAILED totals). Every script in `scripts/` prints such a summary
   when its outputs go to files (`--out`, `> file`).
3. **If the user pastes participant-level data** (rows of a table, Subject IDs with dates, lists of Image IDs), don't
   analyse it. Tell them not to share it with AI tools, and ask for counts instead.
4. **Download links are secrets** (they work without a login). Never ask for them and never read `urls.txt`.
5. **Don't automate IDA.** No browser automation, scraping or calls to IDA's internal endpoints. The user clicks.
   You explain where to click.
6. **Never commit data.** Before any `git add` in a repository that might contain data, check `git status` for CSV,
   ZIP, NIfTI, DICOM or ID lists.

Allowed: reading this repository, the official ADNI/IDA documents and the user's own descriptions, and helping with
**column names**. A header line (`head -1 file.csv`) holds no participant data, but the user should paste it.

## How to guide the user

1. **Start by asking** (one short message): Do they already have ADNI access? What is the project (task, modalities:
   T1 MRI, FLAIR, PET amyloid/tau/FDG, tables only)? Which phases or visits (baseline only or all)? How much disk, and
   laptop or server?
2. **Find where they are** and continue from there:
   0. Rules → `docs/00-rules.md` (always summarize the 5 "must not" points once).
   1. Access → `docs/01-get-access.md`.
   2. Tables → `docs/02-tabular-data.md`.
   3. Image choice → `docs/03-choose-images.md`.
   4. Collection and download → `docs/04-collection-and-download.md`.
   5. Check, unpack, convert → `docs/05-after-download.md`.
   Problems → `docs/06-troubleshooting.md`.
3. **One step at a time.** Give the clicks or commands for the current step, then wait for the result. Don't dump the
   whole guide.
4. **Track progress** in `.adni-progress.md` in this folder (ignored by git): ticked steps, collection names, download
   dates, counts. **Never put participant data or links in it.**
5. **Estimate before big actions**: number of images and GB (about 9 MB per image on average in our download, but
   check the sizes IDA shows), and time (2–18 MB/s for image ZIPs, 0.1–2 MB/s for "dataset" ZIPs in October 2026).
6. **At the end**, remind them: record download dates, keep data off GitHub and AI tools, cite ADNI as the DUA
   requires, and send manuscripts to the ADNI DPC before journal submission.

## Commands you can hand to the user (they run them; outputs stay on disk)

```bash
python scripts/select_one_per_visit.py search.csv --prefer "<regex1>" "<regex2>" --out selected.csv --ids-out wanted_ids.txt
python scripts/ids_to_batches.py wanted_ids.txt --size 500 --out batches.txt
python scripts/find_missing_ids.py wanted_ids.txt collection.csv > missing.txt   # summary on screen, IDs in file
bash   scripts/download_urls.sh urls.txt /path/to/zips
python scripts/check_zips.py /path/to/zips
python scripts/index_images.py /path/to/raw/ADNI --out image_index.csv
bash   scripts/convert_to_nifti.sh /path/to/raw/ADNI /path/to/nifti
python scripts/ida_to_bids.py /path/to/zips --bids /path/to/bids --metadata search.csv --dry-run   # then without --dry-run
```
