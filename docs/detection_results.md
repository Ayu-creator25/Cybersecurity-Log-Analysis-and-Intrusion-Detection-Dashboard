# Detection results

Labels: **verified** = computed from the files; **inference** = reasoned from verified facts; **recommendation** = a proposed choice; **unknown** = not checked.

## 1. Baseline detector: robust z-scores (2026-10-08)

Script: `src/baseline.py`. Split: `src/split.py` (plan decision D19). Scores of every row are written to `data/processed/baseline_scores.csv` (not stored in Git).

**Method.** The detector learns normal behaviour from the 5,580 normal training rows (2019-04-23 and 24). For each of the 80 features it takes the median and a robust spread (1.4826 times the median absolute deviation; if that is 0, the interquartile range divided by 1.349, then the standard deviation, then 1.0). The score of a row is the mean over the 80 features of its absolute robust z-score, capped at 10. Missing values are filled with the training median. The threshold is the 99th percentile of the training scores. Only the test rows (from 2019-04-25: 2,534 normal and 10,252 attack rows) are evaluated.

### 1.1 Results

- **Verified:** ROC-AUC 0.535 (0.5 means no better than chance).
- **Verified:** Average precision 0.838. The share of attack rows in the test set is 0.802, which is what a detector that always says "attack" would reach.
- **Verified:** Threshold 5.60. 2.1% of the normal test rows are flagged (false alarms) and 1.3% of the attack rows are flagged (recall).
- **Verified:** The median score of the training rows is 0.89 and the median score of the normal test rows is 2.72.

| Attack type | Test rows | ROC-AUC against normal test rows | Flagged at the threshold |
|---|---|---|---|
| ddos | 4,608 | 0.223 | 0.1% |
| password | 3,628 | 0.882 | 2.0% |
| xss | 1,269 | 0.641 | 4.2% |
| injection | 612 | 0.635 | 0.2% |
| dos | 120 | 0.430 | 0.0% |
| mitm | 15 | 0.480 | 0.0% |

### 1.2 Reading the results

- **Inference:** Distance from the normal state of the training days is not a good attack signal on this split. Normal rows of the test dates already lie far from the training rows (median score 2.72 against 0.89), which fits the drift in `docs/eda_findings.md` sections 2 and 6.1.
- **Verified:** ddos rows have lower scores than most normal test rows (AUC 0.223). **Unknown:** why.
- **Verified:** password is the only type with clear separation (AUC 0.882), but only 2.0% of its rows pass the threshold. **Inference:** the threshold, set on the training rows, lies above almost all test scores (2.1% of the normal test rows pass it as well), so it cannot separate them.
- **Caution:** dos has only 120 test rows (405 more are not evaluated) and mitm only 15, so their numbers are indicative only. scanning is not evaluated at all (plan decision D19).
- **Unknown:** Whether the weak result comes from the simple method or from the drift. A different detector on the same split will help to tell.

### 1.3 Next steps (recommendations)

1. Run a scikit-learn detector (Isolation Forest) on the same split and compare it with this baseline.
2. Try a reference of normal rows that is close in time to the rows being scored, to see whether the drift is the main problem.
3. Repeat the evaluation with the stricter time-proxy cut-off of 0.5 (`docs/eda_findings.md` section 6.4).
4. Do not choose a threshold or a method by looking at the test results; use the training rows for that.
## 2. Second detector: Isolation Forest (2026-10-09)

Script: `src/isolation_forest.py`. Library: scikit-learn 1.9.1, added to `requirements.txt` (plan decision D18). Same split and same threshold rule as the baseline.

**Method.** Isolation Forest with 200 trees and `random_state` 42, fitted on the 5,580 normal training rows. Missing values are filled with the training median. The score is minus the Isolation Forest score, so a higher score means more unusual. The threshold is the 99th percentile of the training scores. The settings were fixed in advance and not tuned on the test rows. Scores of every row are written to `data/processed/isolation_forest_scores.csv` (not stored in Git).

### 2.1 Comparison on the test rows (2,534 normal and 10,252 attack rows)

| Detector | ROC-AUC | Average precision | False alarms | Recall |
|---|---|---|---|---|
| Baseline (robust z-score) | 0.535 | 0.838 | 2.1% | 1.3% |
| Isolation Forest | 0.563 | 0.819 | 2.8% | 1.8% |

The share of attack rows in the test set is 0.802, which is the average precision of a detector that always says "attack".

| Attack type | Test rows | Baseline: ROC-AUC (flagged) | Isolation Forest: ROC-AUC (flagged) |
|---|---|---|---|
| ddos | 4,608 | 0.223 (0.1%) | 0.351 (0.0%) |
| password | 3,628 | 0.882 (2.0%) | 0.775 (0.2%) |
| xss | 1,269 | 0.641 (4.2%) | 0.723 (13.4%) |
| injection | 612 | 0.635 (0.2%) | 0.572 (0.0%) |
| dos | 120 | 0.430 (0.0%) | 0.540 (0.0%) |
| mitm | 15 | 0.480 (0.0%) | 0.502 (0.0%) |

### 2.2 Reading the results

- **Verified:** Both detectors are close to chance. Neither flags more than 1.8% of the attack rows at its threshold, and false alarms are 2.1% and 2.8%.
- **Verified:** Isolation Forest has the better ROC-AUC (0.563 against 0.535) and the baseline has the better average precision (0.838 against 0.819). The differences are small.
- **Verified:** Isolation Forest is better for xss and dos; the baseline is better for password and injection. For ddos both are below 0.5 (0.351 and 0.223).
- **Verified:** For Isolation Forest the median score is 0.35 on the training rows and 0.46 on the normal test rows, the same pattern as for the baseline (0.89 and 2.72).
- **Caution:** dos has only 120 test rows and mitm only 15, so their numbers are indicative only. scanning is not evaluated (plan decision D19).
- **Inference:** Two very different methods are weak in the same way, so the cause is probably the data and the split rather than one method. Normal behaviour shifts between the training dates and the test dates (`docs/eda_findings.md` sections 2 and 6.1), and many attack rows are not further from normal than the shifted normal rows are.
- **Unknown:** Why ddos rows look more normal than normal rows of the same dates. Also unknown: whether a reference of normal rows that is close in time would change the result.

### 2.3 Next steps (recommendations)

1. Test the drift explanation directly: score each test row against normal rows from the same day, and see whether the results improve.
2. Repeat the evaluation with the stricter time-proxy cut-off of 0.5 (`docs/eda_findings.md` section 6.4).
3. Do not choose a method or a threshold by looking at the test results.
4. Record scikit-learn in the decisions register of the plan at the end of this milestone.


## 3. Drift test: same-day reference (2026-10-09)

Script: `src/drift_test.py`. This is a diagnostic, not a usable detector, because it needs normal rows of the same day.

**Method.** Both detectors (robust z-score baseline and Isolation Forest, same fixed settings as in sections 1 and 2) are run with two references. The far reference is the one used so far: fitted on the normal rows of 2019-04-23 and 24. The same-day reference is fitted on the normal rows of the day that is scored. To avoid scoring rows that the model was fitted on, the normal rows of each day are cut into 5 blocks in time order. Each block is scored by a model fitted on the other 4 blocks, and an attack row gets the average of the 5 models. For every pair of day and attack type, the ROC-AUC of the attack rows is computed against the normal rows of the same day. The far-reference values differ from section 1 and 2 because the comparison group here is the normal rows of the same day, not all normal test rows.

### 3.1 Results (ROC-AUC against the normal rows of the same day)

| Day | Attack type | Attack rows | Normal rows | Baseline, far | Baseline, same day | Forest, far | Forest, same day |
|---|---|---|---|---|---|---|---|
| 04-25 | ddos | 3,009 | 1,179 | 0.170 | 0.694 | 0.215 | 0.794 |
| 04-25 | dos | 120 | 1,179 | 0.312 | 0.246 | 0.423 | 0.196 |
| 04-25 | injection | 612 | 1,179 | 0.569 | 0.606 | 0.474 | 0.588 |
| 04-26 | ddos | 1,599 | 255 | 0.431 | 0.417 | 0.423 | 0.419 |
| 04-26 | password | 2,919 | 255 | 0.902 | 0.859 | 0.826 | 0.866 |
| 04-27 | password | 709 | 342 | 0.848 | 0.943 | 0.728 | 0.935 |
| 04-27 | xss | 1,269 | 342 | 0.534 | 0.675 | 0.591 | 0.725 |
| 04-29 | mitm | 15 | 758 | 0.624 | 0.642 | 0.708 | 0.639 |

Mean ROC-AUC over the pairs, weighted by attack rows: baseline 0.537 (far) and 0.702 (same day); Isolation Forest 0.522 (far) and 0.738 (same day).

### 3.2 Reading the results

- **Verified:** The same-day reference raises the weighted mean ROC-AUC from 0.537 to 0.702 for the baseline and from 0.522 to 0.738 for Isolation Forest.
- **Verified:** The largest gains are ddos on 04-25 (baseline 0.170 to 0.694, forest 0.215 to 0.794), password on 04-27 (0.848 to 0.943 and 0.728 to 0.935) and xss on 04-27 (0.534 to 0.675 and 0.591 to 0.725).
- **Verified:** Some pairs do not improve: dos on 04-25 gets worse (0.312 to 0.246 and 0.423 to 0.196), and ddos on 04-26 stays below 0.5 (0.417 and 0.419).
- **Inference:** The drift in normal behaviour is a main reason for the weak results in sections 1 and 2, but not the only one. Even with a same-day reference the weighted means are only 0.70 to 0.74, and some attack rows still look more normal than normal rows.
- **Caution:** 04-26 has only 255 normal rows, dos 120 attack rows and mitm 15, so these values are indicative only. A real system would need a source of recent normal data, which this diagnostic assumes.
- **Unknown:** Why dos on 04-25 and ddos on 04-26 look more normal than normal rows. Also unknown: how much of the remaining weakness comes from the features chosen, the time-proxy cut-off, or the nature of these attacks.

### 3.3 Next steps (recommendations)

1. Look at the features of the pairs that stay below 0.5 (dos on 04-25, ddos on 04-26) to see what is different there.
2. Repeat the evaluation with the stricter time-proxy cut-off of 0.5 (`docs/eda_findings.md` section 6.4).
3. Do not choose a method or a threshold by looking at the test results.
4. Record scikit-learn in the decisions register of the plan at the end of this milestone.

## 4. Sensitivity to the time-proxy cut-off (2026-10-09)

Script: `src/sensitivity.py`. It uses `src/drift_test.py`, which now reads the cleaned file and accepts a list of features. Same detectors and same fixed settings as before; nothing is tuned on the test rows. This completes item 2 of section 3.3.

**Method.** The feature set depends on one judgment call: a feature is dropped as a time proxy if its absolute Spearman correlation with `ts` among normal rows is at least the cut-off (0.7 so far). Both detectors are run again with three feature sets: no time rule (87 features), cut-off 0.7 (80 features, as used so far) and cut-off 0.5 (69 features). For each set the table shows the ROC-AUC on the test rows with the training rows as reference ("main test", as in sections 1 and 2) and the weighted mean ROC-AUC of the same-day diagnostic from section 3.

### 4.1 Results

| Cut-off | Features | Baseline: main test | Baseline: same-day | Isolation Forest: main test | Isolation Forest: same-day |
|---|---|---|---|---|---|
| none (1.0) | 87 | 0.531 | 0.688 | 0.551 | 0.725 |
| 0.7 (used so far) | 80 | 0.535 | 0.702 | 0.563 | 0.738 |
| 0.5 | 69 | 0.529 | 0.671 | 0.537 | 0.708 |

### 4.2 Reading the results

- **Verified:** With the training rows as reference the ROC-AUC stays between 0.529 and 0.535 for the baseline and between 0.537 and 0.563 for Isolation Forest, whatever the cut-off. With the same-day reference it stays between 0.671 and 0.702 and between 0.708 and 0.738.
- **Verified:** The 0.7 set has the highest value in all four columns. The differences to the other two sets are at most 0.031.
- **Inference:** The conclusions of sections 1 to 3 do not depend on the cut-off: the detectors are weak with the far reference and clearly better with a same-day reference, for every feature set.
- **Caution:** The cut-off of 0.7 was fixed before any detector was run. It is not chosen from these numbers, and it stays. The differences are small and come from the test rows only.
- **Unknown:** Whether other choices (feature scaling, other detectors, a longer or shorter reference window) matter more than the feature set.

### 4.3 Next steps (recommendations)

1. Build the charts and the dashboard from the results so far, and show their limits openly: the weak result with the far reference, the better result with a same-day reference, and the small groups (dos 120 rows, mitm 15 rows, scanning not evaluated).
2. Record the library and decisions of this milestone in the plan (scikit-learn, D18).