# 4. Build a collection and download it

*Last verified: 28 October 2026 (IDA User Manual, June 2026 version, plus our own download of about 34,000 images in
October 2026). Speeds and quirks are what **we** saw. Yours may differ.*

IDA only downloads images that are in a **collection**: search → tick → **Add to Collection** → download the
collection.

## Step 1: add images to a collection
1. Run your search ([step 3](03-choose-images.md)). For a list of Image IDs, paste them in the **Image ID** box of
   Advanced Image Search.
2. On the results tab, tick the images (or the select-all box of the page) → **Add to Collection**.
3. Type a new collection name, or pick an existing collection → **OK**.
   - Keep names short and meaningful, for example `T1_ADNI3_2026Oct`. Short names (up to 25 characters) worked
     for us.
4. Repeat for the next batch, adding to the same collection.

## Step 2: check the collection (don't skip this)
1. **Data Collections** tab → **My Collections** → your collection.
2. Compare the image count with what you wanted. **In our experience IDA occasionally drops a few images** when you
   add large batches (between 5 and 41 out of several thousand, in our case).
3. Click **CSV** to export the list of images in the collection, then find what is missing:
   ```bash
   python scripts/find_missing_ids.py wanted_ids.txt collection_export.csv > missing.txt
   ```
   Paste the missing IDs into Advanced Search again and add them to the same collection.

A collection shows two subsets, **Not Downloaded** and **Downloaded** (images your account has downloaded before).
If you need everything, download both.

## Step 3: choose how to download
| Option | When | What you get |
| --- | --- | --- |
| **1-Click Download** | Small collections (a few GB) | One ZIP, plus a "Download Metadata" link |
| **Advanced Download** | Anything big | Choose a *grouping option* from the drop-down: the collection is split into several ZIPs. Each ZIP has its own link, and you can also get the **list of URLs** |
| **IDA Downloader** | Unstable connection, very large downloads | Official Java (12+) command-line tool that takes the URL list and retries automatically. Instructions come in its README. |

Tips:
- **Smaller ZIPs are safer.** If a 9 GB ZIP fails at 95% you start again. A grouping with more, smaller ZIPs costs
  you less when something breaks.
- **Download one file at a time.** Parallel downloads don't make IDA faster, and stressing the server can get you
  blocked.
- **Download links expire** (about 10 days for us). Create links only when you are ready to download that batch.
- **Treat links like passwords.** They work without logging in, so don't put them in code, notebooks, issues or chat.
- IDA's support page says downloads must be **started and completed on the same computer and IP address used to log
  in** to IDA. Follow that rule.

## Step 4: download with resume (optional helper)
If you have the URL list and use a terminal, [`download_urls.sh`](../scripts/) downloads the links one by one with
`curl`. It resumes partial files, retries, skips finished ones and writes a log:
```bash
bash scripts/download_urls.sh urls.txt /path/to/ADNI_zips
```
The official alternative with the same benefits is the IDA Downloader.

## How long will it take?
What we measured in October 2026, from a university network in Europe:

| ZIP kind | Typical speed |
| --- | --- |
| Image ZIPs (`<collection>.zip`) | 2 to 18 MB/s |
| "Dataset" ZIPs (`<collection>_dataset.zip`, which held all ADNI4 images and derived products such as masks) | 0.1 to 2 MB/s |

About 313 GB took us around **two days**. Split very large downloads into batches (for example one collection per
ADNI phase) so each batch finishes well before its links expire.

## Keep a record
For every batch, write down: collection name, number of images, date the links were created, date of the download,
and the ZIP names. Keep the collection CSV export next to the ZIPs. That is your provenance for the paper.

Next: [5. After the download](05-after-download.md)
