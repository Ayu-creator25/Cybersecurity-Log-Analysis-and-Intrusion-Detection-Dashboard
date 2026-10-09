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