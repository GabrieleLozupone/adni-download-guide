# 2. Download the clinical tables (Study Data)

*Last verified: 28 October 2026. Category and file names are the ones IDA showed on that date.*

Before you touch images, download the tables. They tell you who the participants are, their diagnosis at each visit
and, for imaging, which images the ADNI teams have already checked. Tables are small (tens of MB) and download
directly, with no collection needed.

## How
1. Log in to IDA → **Select Study** → **ADNI**.
2. **DOWNLOAD** menu → **Study Data**.
3. Browse the categories in the left panel, or type a table name in the search box.
4. Tick the tables you want → **Download**. You can also click a table's title to download just that one.

Each file name ends with the date it was generated, for example `DXSUM_28Oct2026.csv`. **That date is your data
version**: keep it in the file name and report it in your paper.

## A starter set
Always take the PDF that sits next to a table (methods or user guide) too.

| Category (left panel) | Table | What it is |
| --- | --- | --- |
| START_HERE → Quick_Start | `DATADIC` | **Data dictionary**: every column of every table and its codes. Open this first. |
| START_HERE → Quick_Start | ADNI Quickstart Guide (PDF) | One-page orientation by ADNI |
| Enrollment → Enrollment | `ROSTER`, `REGISTRY`, `VISITS` | Who is in the study, which visits exist, visit dates |
| Assessments → Diagnosis | `DXSUM` | Diagnosis at each visit. In recent phases `DIAGNOSIS` is 1=CN, 2=MCI, 3=Dementia; older phases use other columns, so check `DATADIC` |
| Subject_Characteristics → Subject_Demographics | `PTDEMOG` | Sex, education, date of birth (year/month), race/ethnicity |
| Assessments → Neuropsychological | `MMSE`, `CDR`, `ADAS`, ... | Cognitive scores |
| Imaging → MR_Image_Quality | `MRIQC` | One row per MRI series, with its LONI Image ID and series type. Very useful for picking images |
| Imaging → MR_Image_Analysis | `UCSFFSX7` | FreeSurfer 7 results with the **Image ID** used and a QC column |
| ADSP_PHC → Image_Analyses | `ADSP_PHC_T1_FS`, `ADSP_PHC_T1_MUSE` | Harmonized MRI measures (ADSP Phenotype Harmonization Consortium) with the Image ID used |
| Study_Info → Data_Database | `ADNIMERGE2` (R package) | Curated merge of key tables; replaces the old `ADNIMERGE.csv` |

Want everything? Downloading all Study Data takes an hour or two (there are a few hundred files, and IDA generates
them on the fly). Download them **one at a time**; don't open many downloads in parallel.

## How ADNI identifies people, visits and time
| Field | Meaning | Use it for |
| --- | --- | --- |
| `RID` | Participant number, the same in every phase | **The person.** Join tables on it and split train/test on it. |
| `PTID` | `SSS_S_RRRR` (site + RID), for example `000_S_0000` (made up) | What IDA calls "Subject ID" for images. Map it to `RID` with `ROSTER`. |
| `PHASE` / `COLPROT` | ADNI1, ADNIGO, ADNI2, ADNI3, ADNI4 | One person can continue across phases ("rollover"). |
| `VISCODE`, `VISCODE2` | Visit labels (`bl`, `m06`, `m12`, ...) | Labels only. Use `VISCODE2` to align phases. |
| `EXAMDATE`, `VISDATE`, `SCANDATE` | Real dates | **Time.** Compute intervals from dates, not from labels. |
| Image ID (`IMAGEUID`, `LONIImage`, `PHC_LONIUID`, ...) | IDA's number for one image | Selecting and finding images ([next step](03-choose-images.md)). |

Two common mistakes:
- **Splitting by visit or by image instead of by `RID`.** The same brain ends up in train and test, and your
  accuracy is inflated.
- **Using information from the future.** For example, a "final diagnosis" column used as the label at baseline.

Next: [3. Choose the images you need](03-choose-images.md)
