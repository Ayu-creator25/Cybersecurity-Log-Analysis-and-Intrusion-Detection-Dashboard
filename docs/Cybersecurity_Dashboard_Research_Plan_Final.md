# Cybersecurity Log Analysis and Intrusion Detection Dashboard
## Research Basis, Dataset Justification, Dataset Provenance, and Basic Project Plan

> **Version 3 (final, updated 2026-10-12).** This document is the research and planning handoff for implementation. It defines the project identity, evidence-backed dataset choice, verified dataset facts, scope, analysis direction, and implementation constraints. Sections 13, 19, 20 and 21 were brought up to date with the repository between 2026-10-07 and 2026-10-12 (rows C23 to C28 in Section 0). It supersedes version 2 (`Cybersecurity_Dashboard_Research_Plan_v2.md`) and keeps every section number of version 1. The draft of version 3 was produced by an external reviewer and then checked again by the implementation agent against the data files and the sources (rows C18 to C21 in Section 0). Changes from version 1 and version 2 are listed in Section 0; work completed so far is in Section 19; decisions are in Section 20; unknowns are in Section 21; Section 22 explains how to verify this document.
>
> **Project name, project area and dataset files are unchanged from version 1. The core stack (Python, Pandas, Plotly, Dash, Git/GitHub) is unchanged.** On 2026-10-08 the user confirmed that further libraries may be added when they make the work easier; each one is listed in `requirements.txt` and in Section 20 (D18). So far `requirements.txt` lists Pandas, NumPy, scikit-learn, Plotly and Dash. The Appendix A verification script uses Pandas only.

---

## 0. Revision summary (version 1 to version 3)

Type key: **REQUIRED** = correction needed for accuracy or safety of the analysis; **OPTIONAL** = improvement; **DECISION** = a choice made by the user or the implementation agent; **UNCHANGED** = stated for clarity.

| ID | Where | Change | Type | Evidence |
|---|---|---|---|---|
| C1 | Sections 1, 2, 3, 4, 6, 8, 10, 11, 12, 15, 17 | Text kept exactly as in version 1 | UNCHANGED | Compared section by section against version 1 on 2026-10-02; these sections are identical |
| C2 | Project identity, stack | Project title, project area, dataset files and the core libraries (Pandas, Plotly, Dash) not changed | UNCHANGED | Version 1 Section 1; the project image (course list, row 23) was inspected by the implementation agent on 2026-10-02 and shows the same title and area (the external reviewer did not have the image) |
| C3 | Section 5 | Added audit facts: timestamp order, time gaps, attack types confined to specific days, whitespace pattern, constant columns, file encoding | REQUIRED | Section 5.1 and Appendix A |
| C4 | Section 7.1 | The 127 vs 124 difference is explained as 3 non-feature columns plus 124 feature columns | OPTIONAL | Column count in Section 5.1 |
| C5 | Section 7.2 | Added exact whitespace pattern and the rule to exclude constant columns from detection inputs | DECISION | Section 5.1; D6 records the exclusion as an implementation decision |
| C6 | Section 7.6 (new) | Added the temporal structure of the data and the rule that time features must not be detector inputs | REQUIRED | Section 5.1 |
| C7 | Section 9, item 5 | "time-based features" limited to context and visualization | REQUIRED | Section 7.6 |
| C8 | Section 7.3 | Added note that attacks are 30.9% of rows, so the anomaly framing must be checked in EDA | OPTIONAL | Label counts in Section 5 |
| C9 | Section 14 | Raw CSV files are committed to Git (user decision); `.gitattributes` protects them from line-ending changes | DECISION | Section 19 |
| C10 | Section 16 | Verification status of each source added | OPTIONAL | Section 16 |
| C11 | Sections 19 to 22, Appendix A | New: work completed, decisions, open items, reviewer instructions, reproduction script | OPTIONAL | This document |
| C12 | Section 16, Section 21 | Verified Sources 3 and 4 and added the full eight-paper citation list from the official UNSW page | OPTIONAL | Official UNSW page; MDPI sources checked on 2026-10-02 |
| C13 | Section 7.3 | Changed the 30.9% “not rare-event” wording so the interpretation is explicitly identified as an inference | REQUIRED | 11,104 / 35,975 = 30.9%; interpretation is not a raw file fact |
| C14 | Sections 5.1, 19, 21 | Marked repository-specific claims that could not be independently checked because the GitHub repository is private | REQUIRED | GitHub URL could not be fetched; screenshot exposes only part of repository state |
| C15 | Section 5.1 | Clarified that the Appendix A script verifies the tabular audit values but does not compute SHA-256 hashes or file encoding; those were checked separately | REQUIRED | Appendix A contains no SHA-256 or byte/encoding calculation; hashes and encoding were independently checked |
| C16 | Section 0 | Updated the revision-summary heading to cover version 1 through version 3 | REQUIRED | This document is now version 3 |
| C17 | Section 14 | Marked the repository-state subsection as user-reported/screenshot-supported rather than independently verified | REQUIRED | Private GitHub repository could not be opened by the external reviewer |
| C18 | Section 0, row C2 | Evidence for the frozen identity restored: the project image was inspected | OPTIONAL | Project image (row 23) |
| C19 | Sections 7.1, 7.3, 16 | Source 3 and Source 4 checked in detail. Source 3 gives 35,975 records and 124 features. Source 4 gives 35,975 records, 125 attributes and a 30.7% attack share. The 0.2-point difference from the local 30.87% is recorded as an open item | OPTIONAL | MDPI pages fetched 2026-10-02 |
| C20 | Section 21, items 2, 3 and 8 | Corrected: the README was uploaded and checked; it holds only the main citation, so the eight-paper list is still to be added. Added the 30.7% vs 30.87% item | REQUIRED | Uploaded `README.md`; GitHub screenshot |
| C21 | Sections 14, 19 | Wording: "this reviewer" replaced by "the external reviewer" so the text stays clear when read later | OPTIONAL | Editorial |
| C22 | Section 13 | Added a progress note (steps 1 and 2 done, step 3 in progress, later steps not started). The development order itself is unchanged | OPTIONAL | Section 19 |
| C23 | Sections 13, 19, 20, 21 | Brought up to date: 26 commits, the scripts and their check results, the cleaning, EDA and feature decisions (D11 to D17), and the open items | REQUIRED | Terminal output from Git Bash; `docs/eda_findings.md`; `docs/feature_set.csv` |
| C24 | Header, Section 20 (D10) | Corrected: NumPy is not "absent". It is installed with Pandas and imported directly by six scripts; at that time `requirements.txt` listed Pandas only (changed again in C25) | REQUIRED | `import numpy` in `src/build_features.py`, `clean_data.py`, `eda_correlation.py`, `eda_separation.py`, `features.py`, `schema_report.py` |
| C25 | Header, Sections 20 and 21, "Suggestion not adopted" | Library policy clarified by the user on 2026-10-08: Pandas, Plotly and Dash stay as the core, and other libraries may be added when they make the work easier. Decisions D1 and D10 reworded, D18 added, the former open item on direct NumPy imports closed, `requirements.txt` now lists NumPy | REQUIRED | User message of 2026-10-08; `requirements.txt` (`pandas==3.0.6`, `numpy==2.5.3`) |
| C26 | Sections 13, 19, 20 | Train/test split added (`src/split.py`, decisions D19 and D20), commit list extended to 27 | OPTIONAL | `python -m src.split`: 9 checks PASS in the user's terminal |
| C27 | Sections 13, 19, 20, 21 | Detector milestone recorded: two detectors, the drift test and the sensitivity check; scikit-learn 1.9.1 added to `requirements.txt` (D18); decisions D21 to D24; open items updated; commit list extended to 32 | OPTIONAL | `docs/detection_results.md`; `requirements.txt`; terminal output from Git Bash |
| C28 | Sections 13, 19, 20, 21 | Charts and dashboard recorded: four Plotly charts, the Dash dashboard with a feature dropdown, the small result files it reads, Plotly 7.1.0 and Dash 4.4.1 in `requirements.txt`; decisions D25 to D28; commit list extended to 35 | OPTIONAL | Terminal output and screenshots supplied by the user; `requirements.txt` |

**Suggestion not adopted:** the course syllabus (CUTM1018) also lists NumPy, Matplotlib and Seaborn. Adding them was suggested as optional. At first this was read as "no new libraries"; on 2026-10-08 the user explained that the core libraries stay and more may be added to make the work easier. NumPy is now listed in `requirements.txt`; Matplotlib and Seaborn are not used yet (Section 20, D18).

---

## 1. Project identity — FROZEN

**Project title:** Cybersecurity Log Analysis and Intrusion Detection Dashboard

**Project area:** Log Analytics, Anomaly Detection

These two values are fixed. Do not rename, reframe, or replace the project idea because of the selected dataset.

The selected dataset is the data source used to implement the existing project idea.

---

## 2. Selected datasets and provenance

### Primary dataset

**File:** `windows10_dataset.csv`

**Dataset family:** TON_IoT (The TON_IoT Datasets)

**Provider/source:** UNSW Canberra, Australian Defence Force Academy / UNSW Research

**Official dataset page:**
https://research.unsw.edu.au/projects/toniot-datasets

The file is the processed Windows 10 dataset from TON_IoT. The official UNSW page states that the Windows datasets were collected using Windows Performance Monitor and include activity related to disk, process, processor, memory, and network behavior. It also states that the processed datasets are provided as CSV files with standardized features and labels.

### Supporting ground-truth dataset

**File:** `GroundTruth_Windows10.csv`

**Source/provenance:** TON_IoT SecurityEvents_GroundTruth data from the same official UNSW dataset family.

The official UNSW page states that the `SecurityEvents_GroundTruth_datasets` contain security events and their timestamps (`ts`). The labels were associated with tagged IP addresses and timestamps in the testbed data.

Official source:
https://research.unsw.edu.au/projects/toniot-datasets

### Project copies

The two files used in this project are local project copies of the selected TON_IoT Windows 10 processed data and its corresponding Windows 10 ground truth:

```text
windows10_dataset.csv
GroundTruth_Windows10.csv
```

The project should preserve the original source attribution in the documentation and should not claim that these files were created by the project.

---

## 3. Why this dataset was selected

The Windows 10 TON_IoT dataset was selected because it gives the project a direct, practical connection between **log/system-activity analytics** and **intrusion detection/anomaly analysis**, while remaining manageable for a university Data Analysis and Visualization project.

### Selection reasons

1. **Direct cybersecurity relevance**
   - UNSW explicitly describes TON_IoT as a dataset for evaluating cybersecurity applications, including intrusion detection systems.
   - This aligns directly with the fixed project title and project area.

2. **Matches the project's log/system-activity analysis direction**
   - The Windows 10 data contains measurements covering processor, process, memory, network, and logical-disk/system activity.
   - This provides multiple interpretable groups of features instead of only a single narrow metric.

3. **Contains labeled normal and attack observations**
   - The processed dataset contains a binary `label` and an event/attack `type`.
   - This makes it possible to compare normal activity with known security-event categories rather than treating every unusual observation as an automatically confirmed attack.

4. **Has an associated ground-truth file**
   - `GroundTruth_Windows10.csv` provides security-event timestamps and attack types.
   - The uploaded files were checked and the ground truth aligns with the attack-labeled observations in the primary dataset.
   - This gives the project a defensible basis for evaluating anomaly/detection results.

5. **Suitable size for the course project**
   - The actual uploaded Windows 10 CSV contains 35,975 rows.
   - This is large enough to support meaningful EDA and detection analysis while being substantially more manageable for a student Dash project than very large cybersecurity datasets containing millions or tens of millions of records.

6. **Good fit for the syllabus**
   - The dataset supports CSV loading, Pandas cleaning, preprocessing, EDA, descriptive statistics, anomaly/outlier analysis, Plotly visualization, and a Dash dashboard.
   - These activities match the supplied Data Analysis and Visualization Using Python syllabus.

7. **Research-supported and academically usable**
   - The official UNSW page grants free use of TON_IoT for academic research in perpetuity and requires citation of the listed TON_IoT papers.
   - The project should preserve those citations in its documentation.

8. **Interpretable for a university demonstration**
   - Feature groups such as processor, memory, process, network, and disk activity can be explained visually and analytically.
   - This supports a dashboard that demonstrates both data-analysis skills and cybersecurity context rather than being a black-box-only model.

### Selection conclusion

The dataset is not selected because it is universally the best cybersecurity dataset. It is selected because its **cybersecurity purpose, Windows system-activity features, labels, ground truth, manageable size, interpretability, and compatibility with the course requirements** make it a strong fit for this specific project.

---

## 4. Source and licensing/use notes

The authoritative source for the dataset is the **UNSW Research TON_IoT dataset page**:

https://research.unsw.edu.au/projects/toniot-datasets

The UNSW page states that:
- TON_IoT can be used for evaluating cybersecurity applications including intrusion detection;
- processed datasets are supplied in CSV format;
- security-event ground truth datasets contain security events and timestamps;
- free use is granted for academic research purposes in perpetuity;
- commercial use requires asking the author;
- users of the dataset are required to cite the eight papers listed on the official page.

Do **not** invent or assign an SPDX-style license such as MIT, Apache-2.0, GPL, or CC-BY unless an authoritative source explicitly states that license. For this project, document the official UNSW academic-use terms and required citations instead.

The principal TON_IoT paper relevant to this Windows dataset is:

Moustafa, N., Keshk, M., Debie, E., & Janicke, H. (2020). *Federated TON_IoT Windows Datasets for Evaluating AI-Based Security Applications*. 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 848–855. DOI: 10.1109/TrustCom50675.2020.00114.

The official UNSW page lists the full set of papers that should be cited when using TON_IoT. The project documentation should follow the official citation requirement rather than inventing a simplified citation policy.

---

## 5. Actual inspection of the uploaded files

The project copies were inspected directly before planning the analysis.

### Main Windows 10 CSV

**File:** `windows10_dataset.csv`

**Rows:** 35,975

**Columns:** 127

**Timestamp column:** `ts`

**Label column:** `label`

**Event/attack-type column:** `type`

**Label distribution:**
- `0` = 24,871
- `1` = 11,104

**Type distribution:**
- normal: 24,871
- ddos: 4,608
- password: 3,628
- xss: 1,269
- injection: 612
- dos: 525
- scanning: 447
- mitm: 15

**Timestamp range:** `1554191661` to `1556547752`

**Unique timestamps:** 35,975

**Exact duplicate rows:** 0

**Pandas-detected null cells:** 0

**Whitespace-only cells:** 3,360

Important: the file contains whitespace-only placeholders in many feature columns. Therefore, although ordinary `isna()` reports zero nulls, data cleaning must explicitly identify whitespace-only values before numerical analysis.

### Ground truth CSV

**File:** `GroundTruth_Windows10.csv`

**Rows:** 11,104

**Columns:** 2

**Columns:** `ts`, `type`

**Exact duplicate rows:** 0

**Pandas-detected null cells:** 0

**Ground-truth event distribution:**
- ddos: 4,608
- password: 3,628
- xss: 1,269
- injection: 612
- dos: 525
- scanning: 447
- mitm: 15

### Ground-truth relationship verified from the uploaded files

The main dataset contains **11,104 attack-labeled rows** and the ground-truth file contains **11,104 rows**.

All 11,104 ground-truth timestamps occur in the main dataset's attack rows, and the attack timestamps are unique in both files.

The main dataset has the following exact relationship:

- `label = 0` -> `type = normal`
- `label = 1` -> one of the seven attack types in the dataset.

This makes the ground truth useful for evaluating detection results.

### 5.1 Additional facts verified in the audit (added in version 2)

The tabular audit values below were computed from the uploaded project copies of the files with the script in Appendix A (run on 2026-10-02). The SHA-256 hashes and encoding/line-ending observations were checked separately from the script. The hashes below are independently verified for the uploaded files. Byte-for-byte identity with the private GitHub repository copies could not be independently verified by the external reviewer.

**File integrity**

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `windows10_dataset.csv` | 37,260,185 | `b66bef4541ad3b4a3c934633b517cf05b29be47d6fd72482d09425b2fff05210` |
| `GroundTruth_Windows10.csv` | 206,346 | `57ab1bf2dd63a64ca82c91ab1592b53eb2fdbcdeced5cf8552b2914516eec171` |

**Encoding:** Both files start with a UTF-8 byte-order mark (BOM, bytes `EF BB BF`) and use Windows line endings (CRLF). Read them with `encoding="utf-8-sig"`.

**Column types:** 52 integer, 5 float and 70 text columns (the text columns are the 69 whitespace-affected feature columns plus `type`). Recent pandas versions display text columns as `str` instead of `object`.

**Whitespace placeholders**
- 3,360 cells contain exactly one space (`" "`), and no other placeholder value exists.
- They are in 69 columns and 761 rows (2.12% of rows).
- 81.3% of them are in `Process_*` columns.
- After replacing them with missing values, every feature column converts to a number. There are no other non-numeric values.

**Feature columns:** 124 in total, grouped by name prefix as Memory 36, Process 28, LogicalDisk 23, Network 22, Processor 15. Together with `ts`, `label` and `type` they make the 127 columns.

**Constant columns:** 19 feature columns have a single value in every row (Network 11, Processor 4, Process 4). They carry no information.

**Column names:** 9 names contain double spaces (all `LogicalDisk(_Total) Avg  Disk ...`), many have inconsistent spaces and underscores, and 3 contain the spelling `ransitions` (`Processor_C1_ransitions_sec`, `_C2_`, `_C3_`). The raw names must stay unchanged in the raw data.

**Timestamps** (`ts` is Unix time in seconds, interpreted as UTC)
- Range: 2019-04-02 07:54:21 to 2019-04-29 14:22:32.
- The file is not sorted by `ts`: 61 rows are out of order.
- The median step between consecutive sorted rows is 10 seconds.
- There are 8 gaps longer than one hour. The largest is 1,660,101 seconds (19.21 days).

**Rows per day and type (UTC date)**

| Date | normal | ddos | dos | injection | mitm | password | scanning | xss |
|---|---|---|---|---|---|---|---|---|
| 2019-04-02 | 5,194 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019-04-03 | 8,640 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019-04-04 | 2,921 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019-04-23 | 3,450 | 0 | 0 | 0 | 0 | 0 | 152 | 0 |
| 2019-04-24 | 2,132 | 0 | 405 | 0 | 0 | 0 | 295 | 0 |
| 2019-04-25 | 1,179 | 3,009 | 120 | 612 | 0 | 0 | 0 | 0 |
| 2019-04-26 | 255 | 1,599 | 0 | 0 | 0 | 2,919 | 0 | 0 |
| 2019-04-27 | 342 | 0 | 0 | 0 | 0 | 709 | 0 | 1,269 |
| 2019-04-29 | 758 | 0 | 0 | 0 | 15 | 0 | 0 | 0 |

Column totals match Section 5 (for example ddos 3,009 + 1,599 = 4,608; password 2,919 + 709 = 3,628). There are no rows on 2019-04-28 or between 2019-04-05 and 2019-04-22.

**Reading of the table (inference):** The first three days (16,755 rows) contain only normal data. Attack types occur only from 2019-04-23 onward, and each type is confined to one or two days. Normal rows on 2019-04-23 to 2019-04-29 total 8,116.

**Ground truth:** The ground-truth file is sorted by `ts` (range 1556025386 to 1556547502), and its 11,104 rows match the main file's attack rows exactly on `ts` and `type`, with no unmatched rows on either side and 0 type mismatches.

---

## 6. Feature structure observed

The Windows 10 dataset contains system-activity measurements grouped around areas such as:

### Processor
Examples:
- `Processor_DPC_Rate`
- `Processor_pct_ Idle_Time`
- `Processor_pct_ User_Time`
- `Processor_pct_ Processor_Time`
- `Processor_pct_ Privileged_Time`
- processor transition/interruption measurements

### Process
Examples:
- process working set
- process page-file activity
- process I/O activity
- process thread count
- process handle count
- process processor/privileged time

### Network
Examples:
- bytes received/sent
- packets received/sent
- packet errors/discards
- TCP RSC activity
- packet rates
- bandwidth

### Memory
Examples:
- available memory
- committed bytes
- page faults
- page reads/writes
- cache activity
- paged/nonpaged pool activity

### Logical disk
Examples:
- disk reads/writes
- disk bytes
- disk queue lengths
- disk transfer activity
- disk idle/read/write percentages

These feature groups provide interpretable material for EDA and feature engineering.

---

## 7. Important dataset limitations / research notes

### 7.1 Dataset version/count discrepancy

The uploaded CSV contains **35,975 rows and 127 columns**.

The 127 columns are 3 non-feature columns (`ts`, `label`, `type`) plus **124 feature columns** (verified, Section 5.1). Published literature commonly reports the TON_IoT Windows 10 subset as **35,975 records and 124 features**, which matches the 124 feature columns. Source 4 reports 125 attributes for the same 35,975-record subset (verified 2026-10-02). How each paper counts `ts`, `label` and `type` was not checked (inference: the 124 figure excludes them).

Therefore:
- use **35,975 rows and 127 columns** when describing the actual uploaded CSV;
- describe the 127 as 3 non-feature columns plus 124 feature columns;
- do not silently change the local file to match a paper's feature count;
- when discussing published statistics, say that the literature may use a different feature-count convention;
- document the actual columns in the project schema.

### 7.2 Data typing requires cleaning

The uploaded CSV was parsed by Pandas with:
- 52 integer columns
- 5 float columns
- 70 object columns

Many measurement columns are numeric-looking strings because the raw CSV contains whitespace-only placeholders. These need explicit cleaning/conversion before statistical analysis.

Verified pattern (Section 5.1): every placeholder is a single space; 3,360 cells in 69 columns and 761 rows. Cleaning rule: replace a whitespace-only value with a missing value, then convert the column to a number. Do not drop the 761 rows before the effect on each class has been checked.

**Constant columns:** 19 feature columns are constant. Keep them in the cleaned data for completeness, but exclude them from detection inputs.

### 7.3 Class imbalance

The normal class is much larger than individual attack categories. This should be acknowledged during EDA and detection evaluation.

The MITM category is especially small (15 rows), so per-class metrics for very small categories must be interpreted cautiously.

Attack-labeled rows are 30.9% of the file (11,104 of 35,975; exactly 30.87%). Source 4 reports 30.7% attack samples for this subset. The difference of about 0.2 percentage points was not explained, and the local file is the authority. Treating this dataset as a rare-event setting would therefore be inappropriate for this project (inference). Unsupervised detectors that assume a small contamination rate may be miscalibrated (inference, to be checked in EDA). Evaluation should report precision, recall and a threshold-free measure such as ROC-AUC or PR-AUC per class, not accuracy alone (recommendation).

### 7.4 Anomaly is not automatically an attack

Anomaly detection should produce anomalous/suspicious/detection-candidate observations. Ground-truth labels can then be used for evaluation. Do not claim that every statistically unusual observation is a confirmed intrusion.

### 7.5 Dataset semantics

This is not a conventional Windows Event Viewer `.evtx` dataset. It is processed Windows system-activity/performance-monitor data from TON_IoT.

The project title remains **Cybersecurity Log Analysis and Intrusion Detection Dashboard**. The documentation should accurately describe the source as Windows system activity / Performance Monitor data where appropriate, rather than falsely calling it Windows Event Log data.

### 7.6 Temporal structure and label leakage (added in version 2)

Facts (Section 5.1): the file is not sorted by `ts`; there are 8 gaps longer than one hour, the largest 19.21 days; the first three days contain only normal rows; each attack type occurs only on one or two specific days.

Consequences (inference and recommendation):
- Sort by `ts` before any time-series chart or rolling calculation.
- Do not treat the data as one continuous time series. Compute rolling features within contiguous segments only.
- Date/day values are strongly associated with the attack schedule and could allow a detector to exploit collection timing rather than system-activity behavior. They must **not** be used as inputs to any detection method. Use them only for exploration and visualization.
- Normal behaviour before 2019-04-23 may differ from normal behaviour during the attack window. Check this in EDA before training any detector on the early normal data only.

### 7.7 File encoding

Both CSV files have a UTF-8 BOM and CRLF line endings. Load them with `encoding="utf-8-sig"`, and do not let Git convert their line endings (Section 14).

---

## 8. Research-backed suitability

The official UNSW source states that TON_IoT was created for evaluating cybersecurity applications including intrusion detection and that its Windows datasets were collected with Performance Monitor from Windows 7 and Windows 10 systems.

The official source also states:
- processed datasets are CSV;
- standardized features and labels are provided;
- feature descriptions/statistics are provided;
- security-event ground truth with timestamps is provided;
- academic research use is granted with required citation of the listed papers.

Published studies independently report the Windows 10 subset at **35,975 records**, supporting the size observed in the uploaded file. Published sources differ in how they count attributes/features, so the local CSV schema should remain the authoritative source for the implementation.

This evidence supports the selected dataset for the project's log analytics and anomaly/intrusion-detection objectives.

---

## 9. Basic project structure

```text
Cybersecurity Log Analysis and Intrusion Detection Dashboard
│
├── 1. Dataset
│   ├── windows10_dataset.csv
│   └── GroundTruth_Windows10.csv
│
├── 2. Data Understanding
│   ├── schema
│   ├── feature groups
│   ├── labels
│   └── timestamp interpretation
│
├── 3. Data Cleaning
│   ├── whitespace/missing-value handling
│   ├── numeric type conversion
│   ├── duplicate checks
│   └── validation
│
├── 4. Exploratory Data Analysis
│   ├── normal vs attack distribution
│   ├── attack-type distribution
│   ├── temporal patterns
│   ├── feature distributions
│   ├── correlations
│   └── normal-vs-attack comparisons
│
├── 5. Feature Engineering
│   ├── time-based features (for context and visualization only; never detector inputs, see 7.6)
│   ├── selected activity indicators
│   └── carefully justified derived features
│
├── 6. Anomaly / Intrusion Detection
│   ├── baseline statistical/rule analysis
│   ├── selected anomaly-detection method
│   ├── anomaly scores/candidates
│   └── comparison with ground truth
│
├── 7. Visualization
│   ├── Plotly charts
│   ├── temporal trends
│   ├── attack distributions
│   └── feature/anomaly views
│
├── 8. Dash Dashboard
│   ├── KPIs
│   ├── filters
│   ├── charts
│   ├── anomaly/detection view
│   └── event/detail table
│
├── 9. Testing
│
├── 10. Documentation
│
└── 11. Deployment / GitHub
```

---

## 10. Recommended analysis questions

The project should answer questions such as:

1. How is normal activity distributed relative to security-event categories?
2. Which attack/event types occur most frequently?
3. How do system-activity measurements differ between normal and attack-labeled observations?
4. What temporal patterns appear in security events?
5. Which feature groups show useful relationships with attack/event categories?
6. Which observations are statistically unusual?
7. How well do the selected detection rules/methods identify known ground-truth events?
8. How can the results be communicated through an interactive cybersecurity dashboard?

These are research questions, not predetermined conclusions.

---

## 11. Detection methodology direction

The implementation should not begin with an unnecessarily complex model.

A sensible research progression is:

1. Establish a transparent baseline using simple statistical or rule-based analysis.
2. Examine whether the data supports an unsupervised anomaly-detection method.
3. Select a method based on the cleaned data, project scope, interpretability, and evaluation requirements.
4. Generate anomaly/detection scores or flags.
5. Compare the results with the known labels/ground truth.
6. Report suitable evaluation metrics and explain their limitations under class imbalance.
7. Keep the final method understandable enough to explain in a university project presentation/report.

The exact algorithm should be selected after EDA and data-quality checks, not hard-coded in advance merely because it is popular.

If a different method is demonstrably more appropriate after data inspection, Claude may recommend the change, explain why, and update the plan before implementation.

---

## 12. Dashboard requirements direction

The final Dash dashboard should communicate the analysis rather than merely display raw tables.

Expected areas include:

- overall record/KPI summary;
- normal vs attack distribution;
- attack/event-type distribution;
- temporal activity/event trends;
- feature-group or feature-level comparisons;
- anomaly/detection results;
- filters for relevant event types or time ranges;
- an event/detail table for investigation;
- clear distinction between observed ground-truth labels and model/statistical detection outputs.

The exact chart set should be decided after EDA so that every visualization answers a real analytical question.

---

## 13. Basic development order

Work in this order unless evidence shows a necessary adjustment:

1. Freeze dataset and project scope.
2. Verify repository/project structure and source files.
3. Inspect and document the raw schema.
4. Build the data-loading layer.
5. Clean/standardize whitespace and numeric fields.
6. Validate the cleaned dataset and ground-truth relationship.
7. Perform EDA.
8. Engineer only justified features.
9. Establish a simple anomaly/detection baseline.
10. Evaluate against the available ground truth.
11. Select/refine the detection approach if justified by evidence.
12. Build Plotly visualizations.
13. Build the Dash dashboard.
14. Test the complete workflow.
15. Document methodology, findings, limitations, dataset provenance, and citations.
16. Prepare GitHub/deployment materials.

Do not jump directly to machine learning or dashboard development before understanding the data.

**Progress (as of 2026-10-12):** steps 1 to 14 are done in a first form: the four Plotly charts and the Dash dashboard are built (the dashboard shows the results of steps 9 to 11 with their limits). Testing of the complete workflow, the final documentation and the deployment preparation are next. See Section 19.

---

## 14. Git/GitHub working principle

Git and GitHub are part of the project workflow, but they should not drive the analytical decisions.

The implementation agent should:
- initialize Git only when the project folder/repository structure is ready;
- make small, meaningful commits after completed milestones;
- keep generated data files out of Git when they are too large or unnecessary, unless the project specifically requires them and repository limits permit it;
- maintain a clear `.gitignore`;
- use a descriptive README with dataset provenance and usage notes;
- create/push the GitHub repository only when the local project state is ready;
- never commit secrets, credentials, environment files containing secrets, or unnecessary generated files;
- keep the commit history understandable enough to demonstrate project progress.

The exact Git/GitHub commands are an implementation concern. The research plan only defines the workflow and documentation expectations.

**Version 2 update (decisions already carried out, Section 19):**
> **Reviewer verification note:** The repository-specific state listed below is based on the user's reported Git/GitHub work and the supplied screenshot. The private GitHub repository itself could not be independently opened by the external reviewer, so these statements remain unverified at the repository level.
- The user reports that the repository is the project folder, with branch `main` and a **private** GitHub repository. The private visibility is visible in the supplied GitHub screenshot; the remaining repository state was not independently opened.
- The two raw CSV files **are committed** in `data/raw/` (user decision). Version 1 allowed this when repository limits permit. The larger file is 37,260,185 bytes (about 36 MB).
- `.gitattributes` contains `data/raw/*.csv -text` so Git never changes their line endings. The committed copies are byte-for-byte identical to the originals (SHA-256 check, Section 19).
- The raw files must never be edited. Cleaned and derived data go in separate folders.
- The UNSW page does not say whether the files may be redistributed. The repository therefore stays private until this is resolved or accepted, and the README credits UNSW, links the official page and carries the citation (Section 21).

---

## 15. Scope boundaries

### In scope
- Windows 10 TON_IoT processed data
- associated Windows 10 ground truth
- log/system-activity analytics
- EDA
- feature engineering
- anomaly detection
- intrusion-detection evaluation
- Plotly
- Dash
- documentation and testing
- Git/GitHub project workflow

### Initially out of scope
- entire TON_IoT collection
- Windows 7 dataset
- Linux dataset
- IoT telemetry
- network dataset
- raw BLG files
- combining multiple TON_IoT modalities
- unnecessarily complex deep-learning pipelines

The project can be expanded later only if there is a demonstrated need and the expansion is justified.

---

## 16. Research sources

### Primary/authoritative
1. **UNSW Research — The TON_IoT Datasets**
   https://research.unsw.edu.au/projects/toniot-datasets

   Use this as the primary source for dataset provenance, collection description, processed-data structure, ground truth, and academic-use/citation requirements.

### Key academic source
2. **Moustafa, N., Keshk, M., Debie, E., & Janicke, H. (2020). Federated TON_IoT Windows Datasets for Evaluating AI-Based Security Applications.**
   IEEE TrustCom 2020, pp. 848–855.
   DOI: 10.1109/TrustCom50675.2020.00114.

### Dataset statistics/context
3. **Analysis of ToN-IoT, UNW-NB15, and Edge-IIoT Datasets Using DL in Cybersecurity for IoT**
   Applied Sciences (2022).
   https://www.mdpi.com/2076-3417/12/19/9572

   Useful for published dataset-size/feature-count context. Do not replace the actual local CSV schema with the paper's feature-count convention.

4. **Adversarial Robustness Evaluation for Multi-View Deep Learning Cybersecurity Anomaly Detection**
   Future Internet (2025).
   DOI: 10.3390/fi17100459.

   Useful as recent research context showing continued use of the TON_IoT Windows 10 subset for cybersecurity anomaly-detection research.

### Full citation list required by the official UNSW page

The official UNSW page asks users of TON_IoT for academic/public use to cite these eight papers:

1. Moustafa, Nour. "A new distributed architecture for evaluating AI-based security systems at the edge: Network TON_IoT datasets." *Sustainable Cities and Society* (2021): 102994.
2. Booij, Tim M., Irina Chiscop, Erik Meeuwissen, Nour Moustafa, and Frank TH den Hartog. "ToN IoT-The role of heterogeneity and the need for standardization of features and attack types in IoT network intrusion datasets." *IEEE Internet of Things Journal* (2021).
3. Alsaedi, Abdullah, Nour Moustafa, Zahir Tari, Abdun Mahmood, and Adnan Anwar. "TON_IoT telemetry dataset: a new generation dataset of IoT and IIoT for data-driven Intrusion Detection Systems." *IEEE Access* 8 (2020): 165130-165150.
4. Moustafa, Nour, M. Keshk, E. Debie and H. Janicke, "Federated TON_IoT Windows Datasets for Evaluating AI-Based Security Applications," 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 2020, pp. 848-855, doi: 10.1109/TrustCom50675.2020.00114.
5. Moustafa, Nour, M. Ahmed and S. Ahmed, "Data Analytics-Enabled Intrusion Detection: Evaluations of ToN_IoT Linux Datasets," 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 2020, pp. 727-735, doi: 10.1109/TrustCom50675.2020.00100.
6. Moustafa, Nour. "New Generations of Internet of Things Datasets for Cybersecurity Applications based Machine Learning: TON_IoT Datasets." *Proceedings of the eResearch Australasia Conference*, Brisbane, Australia. 2019.
7. Moustafa, Nour. "A systemic IoT-Fog-Cloud architecture for big-data analytics and cyber security systems: a review of fog computing." arXiv preprint arXiv:1906.01055 (2019).
8. Ashraf, Javed, Marwa Keshk, Nour Moustafa, Mohamed Abdel-Basset, Hasnat Khurshid, Asim D. Bakhshi, and Reham R. Mostafa. "IoTBoT-IDS: A Novel Statistical Learning-enabled Botnet Detection Framework for Protecting Networks of Smart Cities." *Sustainable Cities and Society* (2021): 103041.

### Verification status of the sources (version 3)
- Source 1 (UNSW page): fetched on 2026-10-02. It supports the Performance Monitor collection on Windows 7 and 10, the CSV format, the ground-truth security events with timestamps (labelled by tagging attacker IPs 192.168.159.30 to 192.168.159.39), free academic use in perpetuity, permission needed for commercial use, and citation of eight listed papers.
- Source 2 (TrustCom 2020 paper): title, authors, venue and DOI match the UNSW page.
- Source 3 (MDPI Applied Sciences 2022): verified on 2026-10-02. It is Applied Sciences 12(19), 9572, DOI 10.3390/app12199572, by Tareq, Elbagoury, El-Regaily and El-Horbaty. It states that the ToN-IoT Windows 10 dataset has 35,975 records and 124 features.
- Source 4 (Future Internet 2025): verified on 2026-10-02. It is Future Internet 17(10), 459, DOI 10.3390/fi17100459, by Li, Qiao and Lee. It uses the TON_IoT Win10 subset (35,975 records, 30.7% attack and 69.3% normal, 125 attributes in five views: memory, process, processor, hard disk activity, network). Its preprocessing converts object-type columns to numbers and fills missing values with the mean. Its focus is adversarial robustness of intrusion detection, which is a different aim from this project, so it is used only as context.
---

## 17. Handoff rules for Claude / implementation agent

Claude should treat this file, the uploaded datasets, and the uploaded project image as the initial project evidence package.

### Before doing implementation work

Claude must first:
1. read this entire plan;
2. inspect the project image and preserve the exact project title and project area;
3. inspect both CSV files rather than assuming their schema from this document;
4. check whether the local files agree with the documented facts;
5. inspect the current project/repository state before creating or changing files;
6. identify any contradiction, missing requirement, risky assumption, or technically incorrect statement.

### If something is wrong

If Claude finds an error in the plan, dataset assumptions, repository structure, or proposed approach:
- stop before making the affected implementation change;
- explain the exact issue;
- provide the evidence or reason;
- propose the smallest appropriate correction;
- update the plan/documentation if that correction is accepted or clearly required;
- then continue only with the corrected plan.

Do not silently ignore an important contradiction.

### Decision-making rule

Claude is expected to make reasonable technical decisions within the project's fixed scope.

If there is a better approach for the project, Claude should:
- identify it;
- explain why it is better using evidence from the dataset, syllabus, project requirements, or current technical constraints;
- distinguish a required correction from an optional improvement;
- avoid changing the fixed project identity;
- avoid unnecessary complexity.

Claude does **not** need permission for every small implementation choice. It should ask for user input only when the decision materially changes the project scope, changes the fixed project identity, requires an external credential/account decision, or has multiple materially different valid paths that cannot be resolved from the evidence.

### One-work-at-a-time rule

Do not implement the entire project in one step.

Work as a sequence of small milestones. At each milestone:
1. state the current objective;
2. inspect the relevant evidence/files;
3. make the smallest necessary changes;
4. validate the result;
5. report what changed and what was verified;
6. identify the next milestone;
7. stop and wait for the user before starting the next major milestone.

The preferred implementation order is the development order in Section 13.

### Git/GitHub rule

Git/GitHub work should also be incremental. Each meaningful completed milestone should have a clean, understandable repository state before moving to the next major stage.

Do not create a GitHub repository, push code, or rewrite history without checking the local project state and confirming that no secrets or inappropriate files are included.

### Dataset integrity rule

Never modify the original source CSVs to hide, overwrite, or silently correct source data. Keep raw source files separate from cleaned/derived data where practical.

### Evidence rule

Separate:
- **Fact:** directly verified from the uploaded files or authoritative source;
- **Research evidence:** supported by an external paper/source;
- **Inference:** reasoned interpretation from the evidence;
- **Recommendation:** proposed project choice;
- **Unknown:** information not yet verified.

Do not present an inference or recommendation as if it were a fact.

---

## 18. Stable project assumptions for implementation

Unless new evidence requires correction, implementation should use these stable assumptions:

- Project title remains **Cybersecurity Log Analysis and Intrusion Detection Dashboard**.
- Project area remains **Log Analytics, Anomaly Detection**.
- Primary data is `windows10_dataset.csv`.
- Ground truth is `GroundTruth_Windows10.csv`.
- The actual uploaded CSV contains 35,975 rows and 127 columns.
- Cleaning must handle whitespace-only placeholders.
- The ground truth aligns with the attack-labeled observations in the uploaded main dataset.
- Detection outputs must be distinguished from confirmed ground-truth attacks.
- The full TON_IoT collection is not required for the initial project.
- Method selection should follow EDA and data-quality validation rather than being predetermined.
- The project should remain understandable, reproducible, testable, and appropriate for the Data Analysis and Visualization Using Python course.

---

## 19. Work completed so far (as of 2026-10-12)

Evidence for this section: the terminal output that the user pasted from Git Bash (each command and its result), screenshots of File Explorer and GitHub, and files the user uploaded. The private GitHub repository itself was not opened by any reviewer, so repository-level statements rest on that output.

**Audit (completed).** The project image, the plan, the syllabus and both CSV files were inspected. The ground-truth file was missing from the first upload and was supplied afterwards; the alignment check then passed. Findings and corrections are in Sections 0, 5.1 and 7.

**Environment**
- Git 2.55.0.windows.3, branch `main`; Python 3.12.3 in a virtual environment (`.venv`, ignored by Git); Pandas 3.0.6, NumPy 2.5.3, scikit-learn 1.9.1, Plotly 7.1.0 and Dash 4.4.1, all listed in `requirements.txt`.
- Local folder: `D:\CUTM\3rd_Sem\DAVP\Project\Cybersecurity_Log_Analysis_and_Intrusion_Detection_Dashboard`.

**GitHub**
- Repository: `https://github.com/Ayu-creator25/Cybersecurity-Log-Analysis-and-Intrusion-Detection-Dashboard`, visibility **Private**, created without a README, `.gitignore` or license.
- Description: "DAVP course project: log analytics and anomaly detection on the TON_IoT Windows 10 dataset, with a Plotly Dash dashboard."

**Repository layout**
- `data/raw/`: the two raw CSV files, committed, byte-for-byte identical to the originals (SHA-256 values in Section 5.1; `.gitattributes` rule `data/raw/*.csv -text`).
- `data/processed/`: `windows10_clean.csv`, `features.csv`, `baseline_scores.csv` and `isolation_forest_scores.csv`, ignored by Git and rebuilt by the scripts.
- `docs/`: this plan, `data_dictionary.csv`, `feature_set.csv`, `eda_findings.md` and `detection_results.md`.
- `results/`: small result tables read by the charts and the dashboard (committed): `detector_overall.csv`, `detector_by_type.csv`, `drift_test.csv`, `rows_per_day.csv`, `feature_series.csv`.
- `src/`: the scripts listed below. Also `README.md`, `requirements.txt`, `.gitignore`, `.gitattributes`.

**Scripts and results** (run from the project folder with `python -m src.<name>`; the results are those printed in the user's terminal)

| Script | Purpose | Result |
|---|---|---|
| `data_loader` | Read both raw files without changing them (`utf-8-sig`) | Shapes (35975, 127) and (11104, 2); first column named `ts` |
| `schema_report` | Write `docs/data_dictionary.csv` | 127 rows; Memory 36, Process 28, LogicalDisk 23, Network 22, Processor 15, meta 3; 3,360 blank cells in 69 columns; 19 constant columns; 0 non-numeric feature columns |
| `check_ground_truth` | Compare the ground truth with the attack rows | 11,104 matched, 0 differences, PASS |
| `blank_report` | Show where the blank cells are | 761 rows with a blank; 2.36% of normal rows and 1.56% of attack rows; 11 rows have all 69 blank-capable columns blank |
| `clean_data` | Write `data/processed/windows10_clean.csv` | 35,975 rows, 129 columns, 13 checks PASS |
| `eda_time`, `eda_drift`, `eda_separation`, `eda_correlation` | Exploratory analysis | Results in `docs/eda_findings.md` |
| `features` | Choose the features a detector may use; write `docs/feature_set.csv` | 80 kept, 19 constant, 18 near-copies, 7 time proxies, 8 checks PASS |
| `build_features` | Write `data/processed/features.csv` | 35,975 rows, 84 columns, 2,954 missing values in 709 rows, 9 checks PASS |
| `split` | Define the train/test split for the detector (`docs/eda_findings.md` 6.4) | Train 5,580 normal rows (2019-04-23/24); test 12,786 rows from 2019-04-25 (2,534 normal, 10,252 attack); 852 attack rows of 04-23/24 not evaluated; 9 checks PASS |
| `baseline` | Robust z-score detector fitted on the training rows | Test rows (2019-04-25 on): ROC-AUC 0.535, average precision 0.838 (attack share 0.802), 2.1% false alarms, 1.3% recall; 5 checks PASS |
| `isolation_forest` | Isolation Forest (scikit-learn), same split and threshold rule | ROC-AUC 0.563, average precision 0.819, 2.8% false alarms, 1.8% recall; 3 checks PASS |
| `drift_test` | Diagnostic: far reference against a same-day reference | Weighted mean ROC-AUC: baseline 0.537 and 0.702, Isolation Forest 0.522 and 0.738; 3 checks PASS |
| `sensitivity` | Repeat with three feature sets (no time rule, cut-off 0.7, cut-off 0.5) | Conclusions unchanged; main-test ROC-AUC 0.529 to 0.563; 3 checks PASS |
| `save_results` | Save the detector and drift-test result tables in `results/` | 3 files; 5 checks PASS |
| `chart_data` | Tables behind the charts (rows per day, saved results, feature series) | 9 checks PASS |
| `charts` | Four Plotly charts as HTML files in `data/processed/charts/` | 8 checks PASS; the user viewed all four charts |
| `save_dashboard_data` | Save the two small tables the dashboard needs (`rows_per_day.csv`, `feature_series.csv`, 957 KB) | 4 checks PASS |
| `dashboard` (with `dashboard_data`) | Dash dashboard: five key-number cards, four tabs, a dropdown for eight features and a box with the limits of the results | Runs at http://127.0.0.1:8050; the user's screenshots show all four tabs and the dropdown |

**Commits (all pushed; 35 at the time of writing)**

| Commit | Message |
|---|---|
| `1751174` | Add .gitignore and .gitattributes |
| `a4fdb68` | Add raw TON_IoT Windows 10 dataset and ground truth |
| `5dd3b82` | Add README with dataset source and citation |
| `5bc0d56` | Add final research plan |
| `186d735` | Add full TON_IoT citation list and link to research plan |
| `ccefc5b` | Add requirements.txt with pandas |
| `6604940` | Add raw data loader |
| `12f83c5` | Add schema report and data dictionary |
| `b2ab54e` | Add ground-truth alignment check |
| `cd7b4d7` | Update README status and add how-to-run |
| `75fdc8a` | Add blank-cell distribution report |
| `94fd49f` | Ignore generated data/processed folder |
| `bbff09b` | Add data cleaning script with validation |
| `4624c3b` | Update README: cleaning step and run instructions |
| `60b4c49` | Add time-distribution EDA script |
| `ecf5f50` | Add normal-behaviour drift EDA script |
| `04c3213` | Add attack-vs-normal separation EDA script |
| `576b4d0` | Add feature correlation EDA script |
| `e421e68` | Add EDA findings document |
| `1078091` | Update README: EDA step and run instructions |
| `81de18f` | Add feature selection (87 kept features) with decision list |
| `44cfe73` | Drop time-proxy features from the feature set (80 kept) |
| `3b30b11` | Add feature table builder with validation |
| `9974779` | Add within-attack-period drift comparison to EDA 2 |
| `3a590fe` | Add post-feature-selection findings to EDA document |
| `aeefa43` | Update README: feature engineering step and run instructions |
| `80a1b3a` | Update research plan to match the repository (decisions D11-D17) |
| `d83541a` | Add train/test split, list numpy, update README and plan (library policy D18) |
| `ba1f50c` | Add baseline detector (robust z-scores) with results and README update |
| `549bd1f` | Add Isolation Forest detector with comparison, scikit-learn in requirements, README update |
| `ea2c44a` | Add drift test (same-day reference) with results and README update |
| `7dd0a31` | Add sensitivity check of the time-proxy cut-off, results and README update |
| `aca3e6c` | Add Plotly chart 1 (attacks per day), plotly in requirements, plan and README update |
| `05d3c17` | Add charts 2 and 3 (detector results, fresh reference), saved result tables and README update |
| `b0cf69a` | Add chart 4 (feature drift over time) and README update |

A file cannot list the commit that adds it, so the commit that contains this updated plan is not in the table.

**README.md** holds the project title and area, the course, the status, the run instructions, the dataset description with the SHA-256 values, the steps to obtain the data, the academic-use terms, the main citation and all eight papers asked for by the UNSW page, and the link to this plan.

**Not done yet:** tests of the complete workflow, the final documentation, the deployment preparation and the decision about publishing the repository.

---

## 20. Decisions register

| ID | Decision | Made by | Reason |
|---|---|---|---|
| D1 | Project title, project area and dataset files stay exactly as in version 1; the core libraries (Pandas, Plotly, Dash) stay too, and other libraries may be added (D18) | User | Fixed project identity |
| D2 | The project folder is the Git repository; branch `main`; GitHub repository private | User | Project workflow |
| D3 | Raw CSV files are committed in `data/raw/` | User | Reproducibility; size is below GitHub's file-size warning threshold (general knowledge, not re-verified in this session) |
| D4 | `.gitattributes` rule `data/raw/*.csv -text` | Implementation agent | CRLF files must not be altered by Git |
| D5 | Time features are not detector inputs | Implementation agent | Label leakage (Section 7.6) |
| D6 | The 19 constant columns are excluded from detection inputs but kept in the cleaned data | Implementation agent | No information content |
| D7 | Evaluation uses `label = 0` from the main file as the normal class; the ground truth is a cross-check | Implementation agent | Ground truth contains no normal rows and is redundant with the attack rows |
| D8 | Loaders read with `encoding="utf-8-sig"` | Implementation agent | BOM in both files |
| D9 | Raw column names stay unchanged; a cleaned-name mapping is added in the cleaned layer (recommendation, optional) | Implementation agent | Names are inconsistent but raw data must stay untouched |
| D10 | NumPy is a listed dependency (`numpy==2.5.3` in `requirements.txt`); six scripts in `src/` import it directly. Matplotlib and Seaborn are not used so far | Implementation agent | Pandas installs NumPy anyway, so the requirements file now matches the imports |
| D11 | Cleaning drops no rows; whitespace-only cells become missing values | Implementation agent | Blanks occur in both classes (2.36% of normal rows, 1.56% of attack rows); dropping the 761 rows would remove 2 of the 15 mitm rows |
| D12 | `data/processed/` is not stored in Git; scripts rebuild it and check the result | Implementation agent | The files are large and fully reproducible |
| D13 | Near-copy rule: absolute Spearman correlation of at least 0.99; keep the feature with the fewest blank cells, and the first in the file on a tie | Implementation agent | `docs/eda_findings.md` section 4; the label is not used |
| D14 | Time-proxy rule: drop a feature whose absolute Spearman correlation with `ts` is at least 0.7 among normal rows in the early or the late period (7 features) | Implementation agent | `docs/eda_findings.md` section 6.2; the cut-off is a judgment call (open item 5) |
| D15 | The final feature set has 80 features (`docs/feature_set.csv`). `features.csv` holds a row id, `ts`, `label`, `type` and the 80 features; missing values stay missing until the detector fills them from training rows | Implementation agent | Avoids using test rows to fill values |
| D16 | The README is updated in the same commit as the work it describes | User | Fewer README-only commits |
| D17 | Raw column names stay unchanged in the cleaned data and in `features.csv`; the cleaned-name mapping suggested in D9 is not built | Implementation agent | All scripts work with the raw names |
| D18 | Library policy: Python, Pandas, Plotly and Dash are the core and stay. Other libraries may be added when they make the work easier. Each one is listed in `requirements.txt` and recorded in this register | User | The user's clarification of 2026-10-08 |
| D19 | Train/test split: train on the normal rows of 2019-04-23 and 24 (5,580 rows); test on every row from 2019-04-25 (2,534 normal, 10,252 attack); the 852 attack rows of 04-23/24 (scanning and most of dos) are not evaluated; the first three days are not used | Implementation agent | Normal behaviour drifts (`docs/eda_findings.md` sections 2 and 6.1), so attack and normal rows are compared on the same dates; training uses normal rows only |
| D20 | Detector progression: first a simple statistical baseline, then a detector from scikit-learn for comparison (the library is added to `requirements.txt` when it is first used) | Implementation agent | Section 11 asks for a transparent baseline first; D18 allows the extra library |
| D21 | scikit-learn 1.9.1 is added to `requirements.txt` for the Isolation Forest | Implementation agent (allowed by D18) | A tested, standard anomaly detector; recorded here as D18 asks |
| D22 | Detector settings are fixed in advance and not tuned on the test rows: baseline score = mean of the capped (10) absolute robust z-scores; Isolation Forest with 200 trees and `random_state` 42; missing values filled with the training median; threshold = 99th percentile of the training scores | Implementation agent | Avoids choosing settings from the test results |
| D23 | Evaluation reports ROC-AUC, average precision (next to the attack share of 0.802), false alarms and recall at the threshold, per attack type, on the split of D19. The same-day reference is a diagnostic, not a detector | Implementation agent | Section 11, item 6; class imbalance and the drift (`docs/detection_results.md`) |
| D24 | The time-proxy cut-off stays at 0.7 | Implementation agent | Fixed before any detector was run; the sensitivity check (cut-offs none, 0.7, 0.5) did not change the conclusions (`docs/detection_results.md` section 4) |
| D25 | Plotly 7.1.0 and Dash 4.4.1 are listed in `requirements.txt` (core libraries of the project) | Implementation agent | Needed for the charts and the dashboard |
| D26 | The charts and the dashboard answer four questions, one tab each (when do the attacks happen, does normal behaviour change, how well do the detectors work, does a fresh reference help) and state the limits of the results on every tab | Implementation agent | Each chart answers a real analytical question; weak results and small groups are shown openly |
| D27 | The dashboard reads only small committed files (`results/*.csv`, `docs/feature_set.csv`) written by `src/save_results.py` and `src/save_dashboard_data.py`, not the large data files | Implementation agent | It runs after a clone and can be deployed; the large data stay out of Git (D12) |
| D28 | The feature dropdown marks four clock-like features as not used by the detectors (disk free space, Memory Cache Bytes, Memory Pool Nonpaged Bytes, Memory System Driver Total Bytes) | Implementation agent | Makes the reason for D14 visible; these are four of the seven time proxies |

---

## 21. Open items and unknowns

1. **Redistribution rights (unknown):** the UNSW page grants academic research use and states commercial-use permission requirements, but it does not expressly grant redistribution/re-publication rights for downloaded CSV files. The repository is private. A decision is needed before it becomes public.
2. **Syllabus coverage (unknown):** the supplied syllabus teaches NumPy, Pandas, Matplotlib, Seaborn, Plotly, Dash, GitHub/project documentation and AI-assisted development. The core stack has no Matplotlib or Seaborn; D18 allows adding them if the course requires them or they help. Whether the assessment requires this project to use every course library is not stated in the supplied syllabus.
3. **Official feature descriptions (open):** the descriptions published by UNSW have not been fetched. `docs/data_dictionary.csv` was built from the data itself (types, blanks, distinct values, range) and says nothing about the meaning of a feature.
4. **Cause of the drift (unknown):** normal behaviour changes between the early and late period and also inside the attack period (`docs/eda_findings.md` sections 2 and 6.1). The cause is not known. The same-day diagnostic shows that the drift explains a large part of the weak detector results (`docs/detection_results.md` section 3).
5. **Detector results (open):** with the training rows as reference both detectors are close to chance (ROC-AUC 0.535 and 0.563); with a same-day reference they reach 0.702 and 0.738. Which further steps would help (a reference window of recent normal rows, other detectors, scaling) is open. A real system would need a source of recent normal data.
6. **Attack share, 30.87% vs 30.7% (open, minor):** Source 4 reports 30.7% for the Windows 10 subset; the local file gives 30.87%. The cause is unknown. The local file is the authority.
7. **mitm (note):** only 15 rows; its results are indicative only.
8. **Rows not evaluated (note):** the 852 attack rows of 2019-04-23/24 (447 scanning and 405 dos) are not in the test set (D19), so scanning has no result and dos only 120 test rows.
9. **Unexplained cases (unknown):** dos on 04-25 and ddos on 04-26 look more normal than normal rows even with a same-day reference (`docs/detection_results.md` section 3).
10. **Deployment (open):** where the dashboard will be hosted and whether the repository becomes public are not decided. Publishing depends on item 1 (re-sharing of the data files).

Closed since version 3 was first written: the charts and the dashboard are built (D25 to D28); the sensitivity of the results to the time-proxy cut-off (`docs/detection_results.md` section 4; D24); the question "is a 30.9% attack share a problem for the choice of method?" was studied with two detectors; the question of direct NumPy imports (NumPy is now listed in `requirements.txt`, D10 and D18); the eight-paper citation list is in the README (commit `186d735`); sources 3 and 4 are verified (Section 16); a local data dictionary exists; the questions "does normal behaviour drift?" and "is a 30.9% attack share a problem for the choice of method?" were studied in the EDA, with the results above.

---

## 22. Instructions for a reviewer

Please check the following and mark each claim as *confirmed*, *contradicted* or *cannot be verified*:

1. The project title and area in Section 1 against the project image (course project list, row 23: "Cybersecurity Log Analysis and Intrusion Detection Dashboard" / "Log Analytics, Anomaly Detection").
2. The source and licensing statements in Sections 2 and 4 against https://research.unsw.edu.au/projects/toniot-datasets and the TrustCom 2020 DOI.
3. Every number in Sections 5 and 5.1, by running Appendix A on the two CSV files. The expected SHA-256 values are in Section 5.1.
4. That each change in Section 0 is justified by the facts in Section 5.1, and that no change alters the title, area, dataset files or the core libraries (Pandas, Plotly, Dash).
5. The Git/GitHub statements in Section 19 against the repository (the 35 commits in the table, private visibility, `data/raw/`, `.gitattributes`, the scripts in `src/` and the files in `docs/`). If the repository is private and cannot be opened, mark repository-specific claims as cannot be independently verified.
6. Anything in this document stated as a fact that is really an inference or a recommendation.

Evidence labels used in this document: **verified** (computed from the files or read from the official page), **inference** (reasoned from verified facts), **recommendation** (a proposed choice), **unknown** (not checked).

---

## Appendix A. Reproduction script

Save as `verify_facts.py` in the repository root and run it with `python verify_facts.py`. It needs Python with pandas only. It reads the raw files and changes nothing.

```python
import pandas as pd
RAW = "data/raw/"
df = pd.read_csv(RAW + "windows10_dataset.csv", low_memory=False, encoding="utf-8-sig")
gt = pd.read_csv(RAW + "GroundTruth_Windows10.csv", encoding="utf-8-sig")
meta = ["ts", "label", "type"]
feat = [c for c in df.columns if c not in meta]
print("shape", df.shape, "| gt", gt.shape, list(gt.columns))
print("dtypes", {k: int(v) for k, v in df.dtypes.astype(str).replace({"str": "text"}).value_counts().items()})
print("nulls", int(df.isna().sum().sum()), "dups", int(df.duplicated().sum()), "ts unique", df.ts.is_unique)
txt = [c for c in df.columns if df[c].dtype != "int64" and df[c].dtype != "float64"]
ws = pd.DataFrame({c: df[c].astype(str).str.strip().eq("") for c in txt})
print("whitespace cells", int(ws.sum().sum()), "cols", int((ws.sum() > 0).sum()), "rows", int(ws.any(axis=1).sum()),
      "pct rows", round(100 * ws.any(axis=1).mean(), 2))
print("whitespace distinct raw values", {repr(v) for c in txt for v in df.loc[ws[c], c].unique()})
proc_share = ws[[c for c in ws.columns if c.startswith("Process_")]].sum().sum() / ws.sum().sum()
print("share of whitespace cells in Process_ cols", round(100 * proc_share, 1))
print("label", df.label.value_counts().to_dict())
print("type", df.type.value_counts().to_dict())
print("crosstab ok", bool(((df.label == 0) == (df.type == "normal")).all()))
def grp(c):
    for p in ["Processor", "Process", "Network", "Memory", "LogicalDisk"]:
        if c.startswith(p): return p
    return "OTHER"
g = pd.Series({c: grp(c) for c in feat})
print("feature groups", g.value_counts().to_dict())
num = df[feat].apply(lambda s: pd.to_numeric(s.astype(str).str.strip().replace("", pd.NA), errors="coerce"))
print("non-numeric junk after blank->NaN:", int((num.isna().sum().sum()) - ws[[c for c in ws.columns if c in feat]].sum().sum()))
const = num.nunique()[lambda s: s <= 1].index
print("constant cols", len(const), g[const].value_counts().to_dict())
t = pd.to_datetime(df.ts, unit="s", utc=True)
print("ts", df.ts.min(), df.ts.max(), t.min(), t.max())
print("out-of-order rows", int((df.ts.diff() < 0).sum()))
s = df.ts.sort_values().diff().dropna()
print("median step", s.median(), "gaps>1h", int((s > 3600).sum()), "largest gap days", round(s.max() / 86400, 2))
print("gaps>1h list (s):", sorted(s[s > 3600].astype(int).tolist(), reverse=True))
d = pd.crosstab(t.dt.date, df.type)
print(d.to_string())
first_attack = df.loc[df.label == 1, "ts"].min()
print("normal rows before first attack", int(((df.label == 0) & (df.ts < first_attack)).sum()),
      "normal rows after", int(((df.label == 0) & (df.ts >= first_attack)).sum()))
print("names with double spaces", sum("  " in c for c in df.columns), "| 'ransitions' names", sum("ransitions" in c for c in df.columns))
att = df[df.label == 1][["ts", "type"]]
m = gt.merge(att, on="ts", how="outer", suffixes=("_gt", "_main"), indicator=True)
print("gt merge", m["_merge"].value_counts().to_dict(), "type mismatches", int((m.dropna().type_gt != m.dropna().type_main).sum()))
print("gt ts range", gt.ts.min(), gt.ts.max(), "sorted", gt.ts.is_monotonic_increasing)
```
