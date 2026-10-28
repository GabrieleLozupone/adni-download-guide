---
name: adni-download
description: Step-by-step guided walkthrough for downloading ADNI data (clinical tables, MRI, PET) from LONI IDA, from the access application to downloaded ZIPs. Use when the user wants to get ADNI data, asks where to start, or is stuck at a step of the IDA process.
---

# Guided ADNI download

You walk the user through `docs/` one step at a time. You **never see their ADNI data**: you give clicks and
commands, they run them, and they paste back only summary counts. The hard rules in `AGENTS.md` apply throughout.

## 1. Intake (one message, then wait)
Ask:
1. Do you already have an approved ADNI account on IDA? (If unsure: does ADNI appear under **Select Study**?)
2. What will you do with the data? (task, for example "predict MCI→AD conversion from T1")
3. Which data: tables only, T1 MRI, other MRI, amyloid/tau/FDG PET? All visits or baseline only? Which phases?
4. Where will you store it (laptop or server) and how much free disk space?

## 2. Read the rules once
Summarize `docs/00-rules.md` in five bullets: no redistribution (even processed), team only, no AI tools with
participant data (including me: never paste data here), record download dates, DPC review before journal submission.
Ask them to confirm the checklist at the end of that page.

## 3. Create the progress file
Create `.adni-progress.md` (git-ignored) with the user's answers (no participant data) and this checklist:
```
- [ ] 0 rules read      - [ ] 1 access approved   - [ ] 2 tables downloaded (date: )
- [ ] 3 image list ready (n images: , est. GB: )   - [ ] 4 collections built (names: )
- [ ] 4 ZIPs downloaded (date: )  - [ ] 5 ZIPs OK  - [ ] 5 indexed/converted
```
Update it after every step.

## 4. Walk the steps
For the current step, open the relevant doc, give the user **only that step's** clicks/commands adapted to their
answers, and wait for the outcome.

- **Access** (`docs/01-get-access.md`): help draft the "proposed use" text from their project description. They submit
  it themselves.
- **Tables** (`docs/02-tabular-data.md`): suggest the starter set plus the tables their task needs (labels, scores,
  QC tables for image choice). They can paste **column headers** if they need help with joins.
- **Image choice** (`docs/03-choose-images.md`): help them pick Way A (search export + `select_one_per_visit.py`) or
  Way B (QC/analysis tables). Write the `--prefer` patterns with them from the *descriptions they report*. For PET,
  one run per tracer. Ask for the summary lines only (images, groups, chosen, unmatched, ties).
- **Collection and download** (`docs/04-collection-and-download.md`): batches with `ids_to_batches.py --out`, add to
  collection, **always check counts** with `find_missing_ids.py ... > missing.txt` (they paste the stderr summary),
  choose Advanced Download with smaller ZIPs for big sets, then `download_urls.sh` or the IDA Downloader. Never ask to
  see the links.
- **After download**: hand over to the `adni-verify-download` skill.

## 5. When something doesn't match
If IDA looks different from the guide, trust what the user sees and the official IDA manual
(<https://ida.loni.usc.edu/explore/jsp/support/IDA_User_Manual.pdf>). Tell them the guide was verified on 28 October
2026 and suggest opening an issue with the date. Check `docs/06-troubleshooting.md` first.
