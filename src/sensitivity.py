"""Sensitivity check: do the conclusions depend on the time-proxy cut-off?

The feature set depends on one judgment call: features whose absolute correlation with
ts among normal rows is at least the cut-off are dropped as time proxies (0.7 so far).
Here the two detectors are run again with three feature sets:
  - no time-proxy rule (cut-off 1.0): the 87 features left after constants and near-copies
  - cut-off 0.7: the 80 features used so far
  - cut-off 0.5: a stricter rule
For each set: the ROC-AUC on the test rows as before (far reference) and the weighted mean
ROC-AUC of the same-day diagnostic (src/drift_test.py). The settings of the detectors are
fixed, and nothing is tuned on the test rows.
"""
import sys

import numpy as np
import pandas as pd

from src.baseline import roc_auc
from src.build_features import FEATURE_LIST, NOT_FEATURES, kept_features
from src.clean_data import OUT_FILE
from src.drift_test import detector_scores, run
from src.split import split_masks

CUTOFFS = [1.0, 0.7, 0.5]


def feature_set(table, cutoff):
    """Features that stay after constants, near-copies and the time rule with this cut-off."""
    trend = table[["trend_with_ts_early", "trend_with_ts_late"]].abs().max(axis=1).fillna(0)
    candidates = (table["reason"].fillna("") != "constant column") & (table["kept_instead"].fillna("") == "")
    return table.loc[candidates & (trend < cutoff), "column"].tolist()


def far_auc(data, features, train, test, name):
    """ROC-AUC on the test rows with the training rows as reference (as in the main results)."""
    s = detector_scores(name, data.loc[train, features], data[features])
    normal = s[test & (data["label"] == 0)]
    attack = s[test & (data["label"] == 1)]
    return round(roc_auc(attack, normal), 3)


if __name__ == "__main__":
    table = pd.read_csv(FEATURE_LIST)
    data = pd.read_csv(OUT_FILE, float_precision="round_trip")
    train, test, _ = split_masks(data[NOT_FEATURES])
    rows = []
    for cutoff in CUTOFFS:
        features = feature_set(table, cutoff)
        pairs = run(features)
        row = {"cut-off": cutoff, "features": len(features)}
        for name in ("baseline", "forest"):
            row[f"{name} far"] = far_auc(data, features, train, test, name)
            row[f"{name} same-day"] = round(float(np.average(pairs[f"{name}_same_day"], weights=pairs["attack_rows"])), 3)
        rows.append(row)
    result = pd.DataFrame(rows)
    print(result.to_string(index=False))
    checks = {
        "cut-off 0.7 gives exactly the 80 features used so far": feature_set(table, 0.7) == kept_features(),
        "cut-off 1.0 gives 87 features": len(feature_set(table, 1.0)) == 87,
        "a stricter cut-off never adds features": bool(result["features"].is_monotonic_decreasing),
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)