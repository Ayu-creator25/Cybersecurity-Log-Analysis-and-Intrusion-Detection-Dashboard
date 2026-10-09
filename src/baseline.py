"""Baseline detector: how far is a row from normal behaviour? (robust z-scores)

Fit on the training rows only (normal rows of 2019-04-23/24, see src/split.py):
  - for each of the 80 features: the median and a robust spread
    (1.4826 x MAD; if that is 0 the IQR / 1.349, then the standard deviation,
    then 1.0 for the 3 features that do not vary at all in the training rows)
  - missing values are filled with the training median
Score of a row = mean over the 80 features of min(|value - median| / spread, 10).
Threshold = 99th percentile of the scores of the training rows (so about 1% of
normal training rows would be flagged). Only test rows (from 2019-04-25) are evaluated.
Scores of all rows are written to data/processed/baseline_scores.csv.
"""
import sys

import numpy as np
import pandas as pd

from src.build_features import NOT_FEATURES, OUT_FEATURES
from src.data_loader import ROOT
from src.split import split_masks

SCORES_FILE = ROOT / "data" / "processed" / "baseline_scores.csv"
CAP = 10.0
THRESHOLD_QUANTILE = 0.99


def fit(train_x):
    """Return (median, spread) of every feature, measured on the training rows."""
    median = train_x.median()
    spread = 1.4826 * (train_x - median).abs().median()
    iqr = (train_x.quantile(0.75) - train_x.quantile(0.25)) / 1.349
    spread = spread.where(spread > 0, iqr)
    std = train_x.std()
    spread = spread.where(spread > 0, std)
    spread = spread.where(spread > 0, 1.0)
    return median, spread


def score(x, median, spread):
    """Mean capped absolute robust z-score of every row."""
    z = ((x.fillna(median) - median) / spread).abs().clip(upper=CAP)
    return z.mean(axis=1)


def roc_auc(positive, negative):
    """Chance that a random positive scores higher than a random negative (from ranks)."""
    ranks = pd.concat([positive, negative], ignore_index=True).rank()
    n1, n0 = len(positive), len(negative)
    return float((ranks.iloc[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def average_precision(positive, negative):
    """Area under the precision-recall curve (average precision)."""
    y = np.r_[np.ones(len(positive)), np.zeros(len(negative))]
    s = np.r_[positive.to_numpy(), negative.to_numpy()]
    y = y[np.argsort(-s, kind="stable")]
    precision = np.cumsum(y) / np.arange(1, len(y) + 1)
    return float((precision * y).sum() / y.sum())


def evaluate(scores, index, train, test, threshold):
    """Return a dict with the overall results and a table per attack type."""
    normal = scores[test & (index["label"] == 0)]
    attack = scores[test & (index["label"] == 1)]
    rows = []
    for attack_type in ["ddos", "password", "xss", "injection", "dos", "mitm"]:
        part = scores[test & (index["type"] == attack_type)]
        rows.append(
            {
                "type": attack_type,
                "rows": len(part),
                "auc_vs_normal": round(roc_auc(part, normal), 3),
                "flagged_percent": round(100 * float((part > threshold).mean()), 1),
            }
        )
    return {
        "overall_auc": round(roc_auc(attack, normal), 3),
        "average_precision": round(average_precision(attack, normal), 3),
        "base_rate": round(len(attack) / (len(attack) + len(normal)), 3),
        "false_alarm_percent": round(100 * float((normal > threshold).mean()), 1),
        "recall_percent": round(100 * float((attack > threshold).mean()), 1),
        "median_train": round(float(scores[train].median()), 2),
        "median_test_normal": round(float(normal.median()), 2),
        "per_type": pd.DataFrame(rows),
    }


def checks(data, scores, train, features, spread):
    """Return a dict of checks (True = passed)."""
    return {
        "80 features used": len(features) == 80,
        "fitted on normal training rows only": bool((data.loc[train, "label"] == 0).all()) and int(train.sum()) == 5580,
        "every row has a score": len(scores) == 35975 and not bool(scores.isna().any()),
        "every spread is above 0": bool((spread > 0).all()),
        "scores are between 0 and the cap": bool(scores.between(0, CAP).all()),
    }


if __name__ == "__main__":
    data = pd.read_csv(OUT_FEATURES)
    features = [c for c in data.columns if c not in NOT_FEATURES]
    index = data[NOT_FEATURES]
    train, test, left_out = split_masks(index)
    median, spread = fit(data.loc[train, features])
    scores = score(data[features], median, spread)
    threshold = float(scores[train].quantile(THRESHOLD_QUANTILE))
    result = evaluate(scores, index, train, test, threshold)

    out = index.assign(score=scores.round(4), split=np.where(train, "train", np.where(test, "test", "left out")))
    out.to_csv(SCORES_FILE, index=False)
    print("written:", SCORES_FILE)
    print("features:", len(features), "| train rows:", int(train.sum()), "| test rows:", int(test.sum()))
    print("threshold (99th percentile of training scores):", round(threshold, 2))
    print()
    print("test results (attack rows against normal rows from 2019-04-25 on):")
    print("  ROC-AUC:", result["overall_auc"], "(0.5 = no better than chance)")
    print("  average precision:", result["average_precision"], "| share of attack rows in the test set:", result["base_rate"])
    print("  normal rows flagged (false alarms):", result["false_alarm_percent"], "%")
    print("  attack rows flagged (recall):", result["recall_percent"], "%")
    print("  median score of training rows:", result["median_train"], "| of test normal rows:", result["median_test_normal"])
    print()
    print(result["per_type"].to_string(index=False))
    print()
    results = checks(data, scores, train, features, spread)
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")
    sys.exit(0 if all(results.values()) else 1)