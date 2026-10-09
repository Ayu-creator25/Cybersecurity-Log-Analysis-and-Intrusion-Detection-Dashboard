"""Second detector: Isolation Forest (scikit-learn), compared with the baseline.

Same split as the baseline (src/split.py): fit on the 5,580 normal training rows,
evaluate on the test rows from 2019-04-25. Missing values are filled with the
training median. Settings are fixed in advance (200 trees, random_state 42) and
are not tuned on the test rows. Score of a row = minus the Isolation Forest score,
so a higher score means more unusual. The threshold is the 99th percentile of the
training scores, the same rule as for the baseline.
Scores of all rows go to data/processed/isolation_forest_scores.csv.
"""
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from src.baseline import THRESHOLD_QUANTILE, evaluate, fit, score
from src.build_features import NOT_FEATURES, OUT_FEATURES
from src.data_loader import ROOT
from src.split import split_masks

SCORES_FILE = ROOT / "data" / "processed" / "isolation_forest_scores.csv"
N_TREES = 200
SEED = 42


def forest_scores(data, features, train):
    """Fit on the training rows and return the score of every row (higher = more unusual)."""
    fill = data.loc[train, features].median()
    x = data[features].fillna(fill)
    model = IsolationForest(n_estimators=N_TREES, random_state=SEED)
    model.fit(x[train])
    return pd.Series(-model.score_samples(x), index=data.index)


def comparison(results):
    """One table with the overall numbers of every detector side by side."""
    rows = {}
    for name, r in results.items():
        rows[name] = {
            "ROC-AUC": r["overall_auc"],
            "average precision": r["average_precision"],
            "false alarms %": r["false_alarm_percent"],
            "recall %": r["recall_percent"],
        }
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    data = pd.read_csv(OUT_FEATURES)
    features = [c for c in data.columns if c not in NOT_FEATURES]
    index = data[NOT_FEATURES]
    train, test, left_out = split_masks(index)

    results, all_scores = {}, {}
    median, spread = fit(data.loc[train, features])
    all_scores["baseline (robust z-score)"] = score(data[features], median, spread)
    all_scores["isolation forest"] = forest_scores(data, features, train)
    for name, s in all_scores.items():
        threshold = float(s[train].quantile(THRESHOLD_QUANTILE))
        results[name] = evaluate(s, index, train, test, threshold)

    forest = all_scores["isolation forest"]
    out = index.assign(score=forest.round(5), split=np.where(train, "train", np.where(test, "test", "left out")))
    out.to_csv(SCORES_FILE, index=False)
    print("written:", SCORES_FILE)
    print("features:", len(features), "| train rows:", int(train.sum()), "| test rows:", int(test.sum()))
    print("share of attack rows in the test set:", results["isolation forest"]["base_rate"], "(what always saying attack would reach as average precision)")
    print()
    print(comparison(results).to_string())
    print()
    print("ROC-AUC per attack type against the normal test rows (flagged % at the threshold):")
    per_type = pd.DataFrame(
        {
            name: r["per_type"].set_index("type").apply(
                lambda row: f"{row['auc_vs_normal']:.3f} ({row['flagged_percent']}%)", axis=1
            )
            for name, r in results.items()
        }
    )
    per_type.insert(0, "rows", results["isolation forest"]["per_type"].set_index("type")["rows"])
    print(per_type.to_string())
    print()
    r = results["isolation forest"]
    print("median score, training rows:", r["median_train"], "| normal test rows:", r["median_test_normal"])
    checks = {
        "fitted on normal training rows only": bool((data.loc[train, "label"] == 0).all()) and int(train.sum()) == 5580,
        "every row has a score": len(forest) == 35975 and not bool(forest.isna().any()),
        "80 features used": len(features) == 80,
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)