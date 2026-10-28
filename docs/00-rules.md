# 0. The rules you agree to

*Last verified: 28 October 2026, against the ADNI Data Use Agreement (DUA) PDF dated April 2026. This page is a
reading aid, not legal advice. The [official DUA](https://adni.loni.usc.edu/wp-content/themes/adni_2023/documents/ADNI_Data_Use_Agreement.pdf)
is the only binding text. ADNI says it can change the terms at any time and posts notices at
<https://adni.loni.usc.edu/news-publications/>.*

When you apply for ADNI you sign the DUA. Breaking it ends your access, and ADNI says it may also seek damages.
For a deep-learning project, these are the points that matter most.

## What you may NOT do

| Rule | In practice |
| --- | --- |
| No redistribution of participant-level data, in any form | Don't put ADNI CSVs, images, NIfTI files, preprocessed tensors, embeddings or "anonymised" derived tables on GitHub, Hugging Face, Kaggle, Zenodo, Google Drive links, and so on. The DUA says this applies "even if it is sufficiently processed or altered and lack ADNI subject codes". |
| No sharing outside your team | Only people in your lab/company who are on your ADNI application may use your copy. Everyone else applies for their own access. |
| No re-identification | Don't try to find out who a participant is, and don't contact participants or site staff about individual results. |
| **No AI tools that may retain data** | Don't paste ADNI data into, or upload it to, ChatGPT or any other third-party AI service that may keep, share or train on inputs. That covers prompts, file uploads, fine-tuning and inference. The DUA says an "opt-out" setting is **not** enough. Tools that guarantee data stay contained, such as models run inside your institution, are allowed. |
| Careful with cloud compute | You may train on cloud GPUs (AWS, Azure, GCP, Runpod, ...), but you must check their terms first so your workflow stays secure. |

## What you MAY do

- Train models on ADNI. The DUA says this is "both permitted and encouraged".
- Publish **summary (not participant-level) results**: tables of means, model metrics, figures of group results.
- Publish code (like this repository) that contains no data.
- Release trained model weights, but first think about whether someone could reconstruct training data from them. The
  DUA warns about this especially for large generative models.
- Share a derived dataset with the community **only through ADNI**: send it to the ADNI study PI with the Derived Data
  Submission Form, and ADNI decides whether to distribute it through LONI.

## What you MUST do when you publish

1. **Record the download date** of your data and report it in the Methods section. ADNI updates tables, so this is
   your data "version".
2. **Abstracts:** cite ADNI as the data source and its funding, as space allows.
3. **Manuscripts:**
   - add "for the Alzheimer's Disease Neuroimaging Initiative*" to the author line, with the standard footnote;
   - include the standard ADNI paragraph in Methods and the funding text in Acknowledgements;
   - **send the manuscript to the ADNI Data and Publications Committee (DPC) before submitting it to a journal.** The
     review is administrative, not scientific, and takes up to about 2 weeks. The steps are in the DUA (IDA → My
     Account → Update on the ADNI line → Publication Update, then email the DPC).
   The exact wording to copy is in the DUA PDF. Don't paraphrase it from memory.
4. **Answer the yearly update request.** Your account expires if you don't.

## Before you start: a 1-minute check

- [ ] I belong to a scientific or educational institution and my project is research or teaching.
- [ ] My storage (laptop, server, cloud) is only reachable by my team.
- [ ] My code repository will not contain data, data-derived files or download links.
- [ ] I will not send ADNI data to third-party AI tools, chat assistants or code assistants.
- [ ] I will write down the date of every download.

Next: [1. Get access](01-get-access.md)
