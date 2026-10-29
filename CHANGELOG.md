# Changelog

Dates are when the guide was checked against the live IDA website and the ADNI documents.

## 2026-10-29 — version 1.1.0
- New `scripts/ida_to_bids.py`: IDA ZIPs or unpacked folders → BIDS (session = acquisition date, PET tracer and
  processing level in the name, IDA masks under `derivatives/`, `images.tsv` index). Adapted from the converter we ran
  on about 34,000 ADNI images; tested here on synthetic data.
- New `CITATION.cff` ("Cite this repository") and a "How to cite" section.

## 2026-10-28 — first version
- Checked against: ADNI Data Use Agreement (April 2026 PDF), IDA User Manual (June 2026 version), ADNI data access
  page, and a full download of about 34,000 ADNI images (ADNI1 to ADNI4) in October 2026.
- Added `AGENTS.md`, `CLAUDE.md` and two Claude Code skills (`adni-download`, `adni-verify-download`). The agent guides
  the user step by step and never reads participant-level data (DUA Appendix A).
