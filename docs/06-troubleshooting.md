# Troubleshooting

*Last verified: 28 October 2026. If your problem isn't here, check the
[IDA User Manual](https://ida.loni.usc.edu/explore/jsp/support/IDA_User_Manual.pdf) or contact IDA support from the
IDA website.*

| Problem | Likely cause | What to do |
| --- | --- | --- |
| ADNI is not in **Select Study** | Application not approved yet, or account expired | Check your email for the decision; renew through **My Account** if expired |
| Image ID search returns fewer images than IDs | Modality or image type not ticked; ID not available to you; typo | Tick all modalities and all three image types; search the missing IDs alone |
| A second search on the same page returns 0 results | The page kept the previous state | Reload Advanced Image Search and search again |
| Collection has fewer images than you added | IDA dropped some during a large add | Export the collection CSV, run `find_missing_ids.py`, re-add the missing |
| "Select all" didn't add anything, or added only one page | Results are shown in pages | Tick page by page, then check the collection count |
| Download link gives 403/404 | The link expired or belongs to another session | Generate the links again from the collection (Advanced Download) |
| Download is extremely slow | "Dataset" ZIPs are slow on the IDA side | Use a grouping with more, smaller ZIPs; download one at a time; use resume (`download_urls.sh` or the IDA Downloader) |
| Partial ZIP after a network drop | Interrupted transfer | Resume with `curl -C -` (what `download_urls.sh` does) or the IDA Downloader |
| "Unsupported compression" or corrupted ZIP when unpacking | The ZIP is Zip64 and your tool is too old, or the ZIP really is broken | Test with `python scripts/check_zips.py`; unpack with `7z` or Info-ZIP `unzip` 6.0; download it again if it fails |
| Study Data download takes many minutes | Tables are generated on request | Wait; download one table at a time |
| You can't find an image you saw in a paper | It's processed by a specific group, or it's in another archive | Look for the group's table in Study Data and use its Image ID column |

## Before asking for help in public
Never post screenshots or logs that show Subject IDs, dates, Image IDs of participants, or download links. Describe
the problem in words.
