"""EDA 3: which features separate each attack type from normal rows?

For each attack type the comparison group is the normal rows from the same UTC
dates, so that the change in normal behaviour found in EDA 2 does not distort it.
Measure: AUC from ranks (the chance that a random attack row has a higher value
than a random normal row). 0.5 = no difference, 1.0 or 0.0 = complete separation.
"""
import numpy as np
import pandas as pd

from src.clean_data import OUT_FILE, feature_columns
from src.eda_drift import HELPER_COLUMNS

STRONG = 0.9  # AUC >= 0.9 or <= 0.1 counts as strong separation


def load_features():
    """Return the cleaned data and the list of non-constant feature columns."""
    full = pd.read_csv(OUT_FILE, float_precision="round_trip").copy()  # copy joins the blocks
    full["date"] = pd.to_datetime(full["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    features = [c for c in feature_columns(full) if c not in HELPER_COLUMNS + ("date",)]
    features = [c for c in features if full[c].nunique() > 1]
    return full, features


def auc_per_feature(attack, normal, features):
    """Rank-based AUC of each feature, attack rows against normal rows."""
    both = pd.concat([attack[features], normal[features]], ignore_index=True)
    ranks = both.rank()
    n1 = attack[features].notna().sum().to_numpy()
    n0 = normal[features].notna().sum().to_numpy()
    rank_sum = ranks.iloc[: len(attack)].sum().to_numpy()
    auc = (rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0)
    return pd.Series(auc, index=features)


def separation_summary(full, features):
    """One row per attack type plus the AUC table of all features."""
    aucs, rows = {}, []
    for attack_type in full.loc[full["label"] == 1, "type"].unique():
        attack = full[full["type"] == attack_type]
        dates = attack["date"].unique()
        normal = full[(full["label"] == 0) & (full["date"].isin(dates))]
        auc = auc_per_feature(attack, normal, features)
        aucs[attack_type] = auc
        strength = (auc - 0.5).abs()
        best = strength.sort_values(ascending=False).index[:3]
        rows.append(
            {
                "type": attack_type,
                "attack_rows": len(attack),
                "normal_rows_same_dates": len(normal),
                "strong_features": int(((auc >= STRONG) | (auc <= 1 - STRONG)).sum()),
                "best_feature": best[0],
                "best_auc": round(float(auc[best[0]]), 3),
                "top3": "; ".join(f"{b} ({auc[b]:.2f})" for b in best),
            }
        )
    summary = pd.DataFrame(rows).sort_values("attack_rows", ascending=False)
    return summary, pd.DataFrame(aucs)


if __name__ == "__main__":
    full, features = load_features()
    summary, aucs = separation_summary(full, features)
    print("features used (constant columns skipped):", len(features))
    print()
    print(summary.drop(columns=["top3"]).to_string(index=False))
    print()
    for _, r in summary.iterrows():
        print(f"{r['type']}: {r['top3']}")
    print()
    strong_any = ((aucs >= STRONG) | (aucs <= 1 - STRONG)).any(axis=1)
    strong_all = ((aucs >= STRONG) | (aucs <= 1 - STRONG)).all(axis=1)
    print("features that separate at least one attack type strongly:", int(strong_any.sum()))
    print("features that separate every attack type strongly:", int(strong_all.sum()))