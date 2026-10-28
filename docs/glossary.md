# Glossary

| Term | Meaning |
| --- | --- |
| **ADNI** | Alzheimer's Disease Neuroimaging Initiative: a longitudinal study (since 2004) with sites in the USA and Canada, with MRI, PET, biomarkers and clinical data |
| **Phases** | ADNI1, ADNIGO, ADNI2, ADNI3, ADNI4: successive grants with different protocols. Participants can continue from one phase to the next |
| **IDA** | LONI Image & Data Archive, the website that hosts and distributes ADNI data |
| **LONI** | Laboratory of Neuro Imaging (University of Southern California), which runs IDA |
| **DUA** | Data Use Agreement, the terms you accept to get ADNI data ([summary](00-rules.md)) |
| **DPC** | ADNI Data and Publications Committee. It reviews your manuscript (administratively) before journal submission |
| **Study Data** | The tables (CSV) and documentation, downloadable directly |
| **Collection** | Your saved list of images on IDA. Images can only be downloaded from a collection |
| **Image ID** | IDA's number for one image (`I000000` in folder names) |
| **Original / Pre-processed / Post-processed** | Image types: as acquired / corrected by ADNI teams / derived products (masks, segmentations) |
| **RID** | Participant number, stable across phases. Use it as the person key |
| **PTID / Subject ID** | `SSS_S_RRRR`: site number + RID |
| **VISCODE / VISCODE2** | Visit labels (`bl`, `m12`, ...). Use real dates for time |
| **CN / MCI / Dementia (AD)** | Cognitively normal / mild cognitive impairment / dementia |
| **ADSP-PHC** | Alzheimer's Disease Sequencing Project Phenotype Harmonization Consortium: harmonized measures, image choices and masks |
| **GradWarp, B1, N3** | MRI corrections (gradient non-linearity, B1 field inhomogeneity, intensity non-uniformity) applied by ADNI to older phases |
| **Zip64** | ZIP format for files over 4 GB. Some old tools can't open it |
