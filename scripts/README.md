# Helper scripts

Small, optional helpers for the manual workflow. They only read files **you** downloaded from IDA and never contact
IDA themselves, except `download_urls.sh`, which downloads the links you copied from your own collection. No
dependencies beyond Python 3.8+ (standard library), `curl`, and [`dcm2niix`](https://github.com/rordenlab/dcm2niix)
for conversion.

| Script | Step | What it does |
| --- | --- | --- |
| `select_one_per_visit.py` | [3](../docs/03-choose-images.md) | From an Advanced Search CSV, keep one image per subject × date × modality using your `--prefer` list |
| `ids_to_batches.py` | [3](../docs/03-choose-images.md) | Split a list of Image IDs into comma-separated batches to paste into the Image ID box |
| `find_missing_ids.py` | [4](../docs/04-collection-and-download.md), [5](../docs/05-after-download.md) | List wanted Image IDs missing from a collection export, search export or image index |
| `download_urls.sh` | [4](../docs/04-collection-and-download.md) | Download a list of ZIP links one at a time, with resume, retries and a log (links are not logged) |
| `check_zips.py` | [5](../docs/05-after-download.md) | Test every ZIP in a folder (Zip64 OK) |
| `index_images.py` | [5](../docs/05-after-download.md) | Build `image_index.csv` (subject, description, date, Image ID, format, path) from the unpacked folders |
| `convert_to_nifti.sh` | [5](../docs/05-after-download.md) | DICOM → `.nii.gz` with dcm2niix, one file per Image ID |
| `ida_to_bids.py` | [5](../docs/05-after-download.md) | ZIPs (or unpacked folders) → BIDS dataset, with `images.tsv` (one row per Image ID: name, grid, orientation, sha256) and `participants.tsv` |

Run each with `--help` (Python) or without arguments (shell) for usage. Tests use only synthetic data:
`python -m unittest discover tests`.

## Adding a script
We add scripts here when one of our own processing steps turns out to be useful to others. Each script:
- runs on files the user downloaded and never contacts IDA (only `download_urls.sh` fetches the user's own links);
- needs only the Python standard library, plus external tools that are named and checked (`curl`, `dcm2niix`);
- prints **counts only** and writes details to files, so an AI agent can read the summary without seeing data;
- treats downloads as untrusted (no paths taken from ZIP member names);
- has a test in `tests/` on synthetic data, a row in the table above, a mention in the guide step where it is used and
  in `AGENTS.md`, and a line in `CHANGELOG.md`; the `version` in `CITATION.cff` goes up.

Never commit your inputs or outputs (CSV exports, ID lists, URL lists, indexes): they are ADNI data or give access to
it. The repository's `.gitignore` blocks the usual file types, but check `git status` before every commit.
