# EDA findings

Date: 2026-10-03. Data: `data/processed/windows10_clean.csv` (built by `src/clean_data.py`).
Scripts: `src/eda_time.py`, `src/eda_drift.py`, `src/eda_separation.py`, `src/eda_correlation.py`.

Labels: **verified** = computed from the files; **inference** = reasoned from verified facts; **recommendation** = a proposed choice; **unknown** = not checked.

## 1. Time structure

- **Verified:** Rows exist on 9 UTC dates only: 2019-04-02, 03 and 04 (all normal, 16,755 rows), then 04-23, 24, 25, 26, 27 and 29. There are no rows between 04-05 and 04-22, and none on 04-28.
- **Verified:** The attack share per day is 0% on the first three days, then 4.2%, 24.7%, 76.0%, 94.7% and 85.3%, and 1.9% on 04-29.
- **Verified:** Each attack type has its own time block (UTC):
  - scanning: 04-23 13:16 to 04-24 06:53
  - dos: 04-24 18:16 to 04-25 02:50
  - injection: 04-25 06:15 to 10:14
  - ddos: 04-25 15:16 to 04-26 07:33
  - password: 04-26 13:47 to 04-27 03:47
  - xss: 04-27 04:56 to 12:40
  - mitm: 04-29 12:22 to 14:18
- **Verified:** There are 8 gaps longer than one hour. The longest is 461.1 hours (04-04 08:06 to 04-23 13:15), the next 47.5 hours.
- **Verified:** From the first attack (2019-04-23 13:16:26 UTC) on, there are 19,218 rows: 8,114 normal and 11,104 attack (57.8% attack).
- **Inference:** Date and time identify the attack type almost by themselves, so they must never be inputs to a detector.

## 2. Normal behaviour changes between the early and late period

- **Verified:** 16,757 normal rows come before the first attack ("early") and 8,114 after it ("late").
- **Verified:** For 105 non-constant features, the median share of late normal values outside the range holding the middle 98% of early normal values is 0.3%. 20 features have more than 10% outside and 13 have more than 50%.
- **Verified:** Average share outside by group: Process 27.8%, Memory 13.0%, Processor 5.1%, Network 2.4%, LogicalDisk 1.0%.
- **Verified:** Examples (early median to late median): process thread count 996 to 1,540; process handle count 38,831 to 58,076; available memory 516 MB to 1,401 MB.
- **Unknown:** The cause (for example more programs running, a restart or a different setup).
- **Inference:** A detector trained only on the early normal rows would flag many late normal rows as odd.
- **Recommendation:** Compare attacks with late normal rows, and do not train on the early days alone.

## 3. Which features separate each attack type from normal rows

Method: rank-based AUC for each of the 105 features, attack rows against normal rows from the same UTC dates. 0.5 = no difference; at least 0.9 or at most 0.1 counts as strong.

| Type | Attack rows | Normal rows (same dates) | Strong features | Best feature (AUC) |
|---|---|---|---|---|
| ddos | 4,608 | 1,434 | 4 | Process_Handle Count (0.046) |
| password | 3,628 | 597 | 8 | Memory Cache Bytes (0.955) |
| xss | 1,269 | 342 | 0 | Memory Pool Nonpaged Bytes (0.899) |
| injection | 612 | 1,179 | 1 | Memory System Driver Total Bytes (0.914) |
| dos | 525 | 3,311 | 1 | Network_I(Intel R _82574L_GNC)TCP_APS (0.970) |
| scanning | 447 | 5,582 | 0 | Process_IO_Write Operations_sec (0.895) |
| mitm | 15 | 758 | 0 | Process_Virtual_Bytes (0.839) |

- **Verified:** 14 features separate at least one attack type strongly. No feature separates all types.
- **Inference:** No single feature is enough, so a detector has to combine many features.
- **Caution:** mitm has only 15 rows. Comparing on the same dates does not remove drift within a day, so these scores are hints, not proof.

## 4. Near-copy features

- **Verified:** Among 105 features there are 5,460 pairs. 22 pairs have an absolute Spearman correlation of at least 0.99 and 80 pairs at least 0.90.
- **Verified:** At 0.99 the features form 87 groups: 73 single features, 11 pairs, 2 groups of three and 1 group of four.
- **Verified:** Examples: Memory Available Bytes, KBytes and MBytes (same measure in different units); four LogicalDisk read measures.
- **Recommendation:** Keep one feature per group (about 87 features).

## 5. What this means for the next steps (recommendations)

1. Never use `ts`, date or hour as an input to a detector.
2. Leave out the 19 constant columns and keep one feature per near-copy group.
3. Handle the roughly 20 features that drift between the periods on purpose, and decide how in the feature-engineering step.
4. Evaluate with the `label` and `type` columns of the main file. Report precision and recall per attack type, not accuracy alone, and treat mitm (15 rows) with great care.

## 6. Update after the feature selection (2026-10-07)

Scripts: `src/eda_drift.py` (second comparison), `src/features.py`, `src/build_features.py`. This section adds to sections 2 and 5.

### 6.1 Normal behaviour also changes inside the attack period

- **Verified:** Normal rows of 2019-04-23 and 24 (5,580 rows) compared with normal rows of 2019-04-25 to 29 (2,534 rows): 32 features have more than 10% of their values outside the first range, 6 have more than 50%, and the median share outside is 3.6%. The comparison in section 2 (early against late) gave 20 features and 13 features.
- **Inference:** The state of the machine changes steadily over time. It is not a single step between two periods.

### 6.2 Some features work like clocks

- **Verified:** Among the 87 features left after removing constant columns and near-copies, 7 have an absolute Spearman correlation with `ts` of at least 0.7 among normal rows, in the early period or in the late period (early / late):
  - LogicalDisk(_Total) pct_ Free Space: -0.95 / -0.98
  - Memory System Driver Total Bytes: 0.92 / 0.02
  - Memory Pool Nonpaged Bytes: 0.80 / 0.21
  - Memory Cache Bytes: -0.32 / -0.79
  - Memory System Cache Resident Bytes: 0.14 / -0.79
  - Memory Pool Paged Resident Bytes: -0.28 / -0.78
  - Memory Standby Cache Normal Priority Bytes: -0.15 / -0.72
- **Inference:** A detector could read the time from these features. Each attack type has its own time block (section 1), so the time would give away the attack type without any real detection.
- **Verified:** The best feature of password (Memory Cache Bytes), injection (Memory System Driver Total Bytes) and xss (Memory Pool Nonpaged Bytes) in section 3 are among these 7 features.
- **Inference:** The separation scores of those three attack types are partly a time effect.
- **Unknown:** Whether the cut-off of 0.7 is the best one. It is a judgment call.

### 6.3 Final feature set

- **Verified:** Of the 124 measurement columns, 80 are kept, 19 are constant, 18 are near-copies of a kept feature and 7 are time proxies. The 80 kept features are Memory 25, Process 20, LogicalDisk 16, Processor 10 and Network 9. Every column with its reason is in `docs/feature_set.csv`.
- **Verified:** `src.build_features` writes `data/processed/features.csv` with 35,975 rows and 84 columns (row id, `ts`, `label`, `type` and the 80 features). It holds 2,954 missing values in 709 rows.
- **Decision:** `ts`, `label` and `type` are never features. Missing values stay missing, and the detector fills them using training rows only.

### 6.4 Consequences for the evaluation (recommendations)

1. Compare each attack type with normal rows from the same dates, and report results for each attack type separately.
2. Repeat the main evaluation once with a stricter time-proxy cut-off of 0.5, to see whether the conclusions depend on the 0.7 choice.
3. Do not train a detector on the first three days alone.
4. Treat the results for mitm (15 rows) as indicative only.