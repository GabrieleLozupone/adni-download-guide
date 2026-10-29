# ADNI download guide: how to download the ADNI dataset from LONI IDA

[![DOI](https://zenodo.org/badge/1437210919.svg)](https://doi.org/10.5281/zenodo.23769997)

A plain, step-by-step guide to getting **ADNI** (Alzheimer's Disease Neuroimaging Initiative) data (clinical tables and MRI/PET images) out of the
**LONI Image & Data Archive (IDA)**, written for machine-learning and deep-learning researchers who have never used
IDA before.

> **Last verified: 28 October 2026.** IDA and the ADNI rules change often. Everything here worked on that date;
> buttons, menus and limits may be different when you read this. If something no longer matches, the official
> sources linked below are always right, and this guide may be out of date.
>
> This is an **unofficial** guide. It is not affiliated with, reviewed or endorsed by ADNI, LONI or the University of
> Southern California. It contains **no ADNI data** of any kind. You need your own approved ADNI account.

## The whole process in one picture

```
 1. Rules       2. Access         3. Tables          4. Choose images     5. Collection        6. After
 read the  -->  apply on IDA -->  download Study -->  decide which    -->  add images to  -->  test ZIPs,
 DUA            (~2 weeks)        Data (CSV)         Image IDs you        a collection,       unpack,
                                                     need                 download ZIPs       convert
```

| Step | Guide | Time |
| --- | --- | --- |
| 0 | [Rules you agree to (read this first)](docs/00-rules.md) | 10 min |
| 1 | [Get an IDA account and ADNI access](docs/01-get-access.md) | ~2 weeks of waiting |
| 2 | [Download the clinical tables (Study Data)](docs/02-tabular-data.md) | 1 hour |
| 3 | [Choose the images you need](docs/03-choose-images.md) | 1 hour to 1 day |
| 4 | [Build a collection and download it](docs/04-collection-and-download.md) | hours to days |
| 5 | [After the download: check, unpack, convert](docs/05-after-download.md) | hours |
| – | [Troubleshooting](docs/06-troubleshooting.md) · [Glossary](docs/glossary.md) | |

## The five things people get wrong

1. **Images can only be downloaded from a collection.** You search, tick images, "Add to Collection", then download
   the collection. There is no direct "download all of ADNI" button.
2. **ADNI has many images per visit** (repeats, different processing levels, localizers). Decide your rule *before*
   searching, usually one image per participant, visit and modality.
3. **The participant is `RID`, not the visit label.** Split train/test by participant, and use real dates for time.
4. **Download links expire** (about 10 days in our experience), and big collections take days. Plan the order.
5. **Never put ADNI data into public AI tools** (ChatGPT and similar). The current Data Use Agreement forbids it.
   See [the rules](docs/00-rules.md).

## Helper scripts (optional)
The guide works with only a browser. The [scripts](https://github.com/GabrieleLozupone/adni-download-guide/tree/main/scripts) are small, dependency-free helpers for the boring parts
that run **on files you have already downloaded yourself**: splitting long Image ID lists, keeping one image per visit,
finding images missing from a collection, downloading ZIP links with resume, testing ZIPs, indexing the unpacked
images and converting them to **BIDS** (`ida_to_bids.py`). Requirements: Python 3.8+, `curl`, and optionally [`dcm2niix`](https://github.com/rordenlab/dcm2niix).

## Using an AI agent as your guide (optional)
Open this folder with a coding agent and ask "help me download ADNI". It will interview you, take you through the steps
one at a time and keep a private checklist in `.adni-progress.md`.

- [`AGENTS.md`](AGENTS.md): instructions for any agent that reads it (Codex, Cursor, Gemini CLI, ...).
- [`CLAUDE.md`](https://github.com/GabrieleLozupone/adni-download-guide/blob/main/CLAUDE.md) and two Claude Code skills: [`adni-download`](https://github.com/GabrieleLozupone/adni-download-guide/blob/main/.claude/skills/adni-download/SKILL.md) (guided
  walkthrough) and [`adni-verify-download`](https://github.com/GabrieleLozupone/adni-download-guide/blob/main/.claude/skills/adni-verify-download/SKILL.md) (checks after the download).

**The agent never sees your data.** The ADNI DUA forbids giving participant-level data to third-party AI tools, so
the agent is told to give you commands to run yourself and to read back only summary counts. You are still
responsible: don't paste tables, IDs, dates or download links into the chat, and keep ADNI data in folders the agent
doesn't need to access.

## Official sources (always check these first)

- ADNI data access page: <https://adni.loni.usc.edu/data-samples/adni-data/>
- ADNI Data Use Agreement (PDF): <https://adni.loni.usc.edu/wp-content/themes/adni_2023/documents/ADNI_Data_Use_Agreement.pdf>
- ADNI Data Sharing & Publication Policy (PDF): <https://adni.loni.usc.edu/wp-content/themes/adni_2023/documents/ADNI_DSP_Policy.pdf>
- IDA User Manual (PDF): <https://ida.loni.usc.edu/explore/jsp/support/IDA_User_Manual.pdf>
- IDA login: <https://ida.loni.usc.edu/login.jsp>

## Contributing
Found something that changed? Please open an issue or a pull request and say **the date** you checked. Never attach
ADNI data, screenshots that show participant information, or your download links (they work without a login).

## How to cite
If this guide or its scripts helped your work, please cite it. GitHub shows a **"Cite this repository"** button in the
right sidebar (from [`CITATION.cff`](https://github.com/GabrieleLozupone/adni-download-guide/blob/main/CITATION.cff)),
with APA and BibTeX. The DOI [10.5281/zenodo.23769997](https://doi.org/10.5281/zenodo.23769997) (Zenodo)
always points to the latest version:

```bibtex
@software{lozupone_adni_download_guide,
  author  = {Lozupone, Gabriele},
  title   = {{ADNI download guide: how to download the ADNI dataset from LONI IDA, with helper scripts}},
  year    = {2026},
  version = {1.1.0},
  doi     = {10.5281/zenodo.23769997},
  url     = {https://doi.org/10.5281/zenodo.23769997}
}
```
This is in addition to what ADNI requires: the ADNI acknowledgement and authorship rules in the Data Use Agreement and
the Data Sharing & Publication Policy linked above.

## License
Text and scripts: [MIT](https://github.com/GabrieleLozupone/adni-download-guide/blob/main/LICENSE). ADNI data are governed only by the ADNI Data Use Agreement.
