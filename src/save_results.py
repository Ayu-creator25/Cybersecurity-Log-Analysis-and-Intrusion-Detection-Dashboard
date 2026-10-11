"""Save the result tables that the charts and the dashboard read (small CSV files in results/).

The detectors and the drift test are run once here, so that the dashboard does not
have to repeat a calculation that takes about a minute.
"""
import sys

import numpy as np
import pandas as pd

from src.baseline import THRESHOLD_QUANTILE, evaluate, fit, score
from src.build_features import NOT_FEATURES, OUT_FEATURES
from src.data_loader import ROOT
from src.drift_test import run as run_drift_test
from src.isolation_forest import forest_scores
from src.split import split_masks

RESULTS_DIR = ROOT / "results"
FILES = ["detector_overall.csv", "detector_by_type.csv", "drift_test.csv"]


def detector_tables():
    """Return (overall, by_type): the main-protocol results of both detectors."""
    data = pd.read_csv(OUT_FEATURES)
    features = [c for c in data.columns if c not in NOT_FEATURES]
    index = data[NOT_FEATURES]
    train, test, _ = split_masks(index)
    median, spread = fit(data.loc[train, features])
    all_scores = {
        "baseline (robust z-score)": score(data[features], median, spread),
        "isolation forest": forest_scores(data, features, train),
    }
    overall, by_type = [], []
    for name, s in all_scores.items():
        threshold = float(s[train].quantile(THRESHOLD_QUANTILE))
        r = evaluate(s, index, train, test, threshold)
        overall.append(
            {
                "detector": name,
                "roc_auc": r["overall_auc"],
                "average_precision": r["average_precision"],
                "attack_share_in_test": r["base_rate"],
                "false_alarm_percent": r["false_alarm_percent"],
                "recall_percent": r["recall_percent"],
            }
        )
        by_type.append(r["per_type"].assign(detector=name))
    return pd.DataFrame(overall), pd.concat(by_type, ignore_index=True)[["detector", "type", "rows", "auc_vs_normal", "flagged_percent"]]


if __name__ == "__main__":
    RESULTS_DIR.mkdir(exist_ok=True)
    overall, by_type = detector_tables()
    drift = run_drift_test()
    overall.to_csv(RESULTS_DIR / FILES[0], index=False)
    by_type.to_csv(RESULTS_DIR / FILES[1], index=False)
    drift.to_csv(RESULTS_DIR / FILES[2], index=False)
    for name in FILES:
        print("written:", RESULTS_DIR / name)
    weights = drift["attack_rows"]
    same_day = {n: round(float(np.average(drift[f"{n}_same_day"], weights=weights)), 3) for n in ("baseline", "forest")}
    checks = {
        "all 3 files exist": all((RESULTS_DIR / name).exists() for name in FILES),
        "overall: 2 detectors, ROC-AUC 0.535 and 0.563 (as in detection_results.md)": overall["roc_auc"].tolist() == [0.535, 0.563],
        "by type: 2 detectors x 6 attack types": len(by_type) == 12,
        "drift test: 8 pairs": len(drift) == 8,
        "drift test: weighted same-day ROC-AUC 0.702 and 0.738 (as in detection_results.md)": same_day == {"baseline": 0.702, "forest": 0.738},
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)