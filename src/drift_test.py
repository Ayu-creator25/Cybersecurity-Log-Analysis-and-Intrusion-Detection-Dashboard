"""Diagnostic: is the drift in normal behaviour the reason why the detectors are weak?

Far reference (as before): fit on the normal rows of 2019-04-23/24, score the test rows.
Same-day reference: for each test day, fit on the normal rows of THAT day only.
  To avoid scoring rows that the model was fitted on, the normal rows of the day are
  cut into 5 blocks in time order. Each block is scored by a model fitted on the other
  4 blocks. An attack row gets the average of the 5 models.
Both references use the same two detectors and the same fixed settings as before.
This is a diagnostic, not a usable detector: it needs normal rows of the same day.
Evaluation: for every pair (day, attack type), the ROC-AUC of the attack rows
against the normal rows of the same day.
"""
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from src.baseline import fit, roc_auc, score
from src.build_features import NOT_FEATURES, kept_features
from src.clean_data import OUT_FILE
from src.isolation_forest import N_TREES, SEED
from src.split import split_masks

BLOCKS = 5


def detector_scores(name, fit_x, score_x):
    """Fit a detector on fit_x (normal rows) and return the scores of score_x."""
    fill = fit_x.median()
    if name == "baseline":
        median, spread = fit(fit_x)
        return score(score_x, median, spread)
    model = IsolationForest(n_estimators=N_TREES, random_state=SEED)
    model.fit(fit_x.fillna(fill))
    return pd.Series(-model.score_samples(score_x.fillna(fill)), index=score_x.index)


def same_day_scores(name, normal_x, attack_x):
    """Scores of the normal rows (each by a model that did not see it) and of the attack rows."""
    normal_scores = pd.Series(index=normal_x.index, dtype="float64")
    attack_total = pd.Series(0.0, index=attack_x.index)
    for block in np.array_split(np.arange(len(normal_x)), BLOCKS):
        held_out = normal_x.index[block]
        rest = normal_x.drop(index=held_out)
        normal_scores[held_out] = detector_scores(name, rest, normal_x.loc[held_out])
        attack_total += detector_scores(name, rest, attack_x)
    return normal_scores, attack_total / BLOCKS


def run(features=None):
    """Return a DataFrame with one row per (day, attack type) and the four AUC values.

    features: names of the features to use; the 80 kept features if None.
    """
    data = pd.read_csv(OUT_FILE, float_precision="round_trip")
    features = features or kept_features()
    index = data[NOT_FEATURES]
    train, test, _ = split_masks(index)
    day = pd.to_datetime(data["ts"], unit="s", utc=True).dt.strftime("%m-%d")
    far = {name: detector_scores(name, data.loc[train, features], data[features]) for name in ("baseline", "forest")}
    rows = []
    for d in sorted(day[test].unique()):
        in_day = test & (day == d)
        normal_x = data.loc[in_day & (data["label"] == 0), features]
        attack_x = data.loc[in_day & (data["label"] == 1), features]
        near = {name: same_day_scores(name, normal_x, attack_x) for name in ("baseline", "forest")}
        for attack_type in sorted(data.loc[in_day & (data["label"] == 1), "type"].unique()):
            of_type = data.index[in_day & (data["type"] == attack_type)]
            row = {"day": d, "type": attack_type, "attack_rows": len(of_type), "normal_rows": len(normal_x)}
            for name in ("baseline", "forest"):
                row[f"{name}_far"] = round(roc_auc(far[name][of_type], far[name][normal_x.index]), 3)
                row[f"{name}_same_day"] = round(roc_auc(near[name][1][of_type], near[name][0]), 3)
            rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    table = run()
    print(table.to_string(index=False))
    print()
    weights = table["attack_rows"]
    for name in ("baseline", "forest"):
        far_mean = float(np.average(table[f"{name}_far"], weights=weights))
        near_mean = float(np.average(table[f"{name}_same_day"], weights=weights))
        print(f"{name}: mean ROC-AUC over the pairs (weighted by attack rows): far reference {far_mean:.3f}, same-day reference {near_mean:.3f}")
    checks = {
        "8 pairs of day and attack type": len(table) == 8,
        "all attack rows of the test days are covered (10,252)": int(table["attack_rows"].sum()) == 10252,
        "all AUC values are between 0 and 1": bool(table.filter(like="_far").stack().between(0, 1).all() and table.filter(like="_same_day").stack().between(0, 1).all()),
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)